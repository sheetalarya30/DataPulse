import json
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.pipeline import PipelineRun, ExecutionLog
from app.models.quality import QualityCheckResult
from app.models.incident import Incident
from app.diagnosis.rule_diagnosis import RuleDiagnosisEngine


class AIDiagnosisService:
    """
    Intelligent diagnosis service that uses verified execution logs, error messages,
    and data-quality results to produce forensic explanations.
    Supports configurable AI providers (Gemini, OpenAI) with a reliable Rule-Based fallback.
    """

    @classmethod
    def diagnose(cls, db: Session, run_id: str) -> Optional[Incident]:
        # Always run RuleDiagnosisEngine first to assemble ground-truth facts & evidence
        baseline_incident = RuleDiagnosisEngine.diagnose_run(db, run_id)
        if not baseline_incident:
            return None

        # If AI provider is set to rule_based or no API key provided, return verified baseline
        provider = settings.AI_PROVIDER.lower()
        api_key = settings.AI_API_KEY

        if provider == "rule_based" or not api_key:
            logger.info(f"Using deterministic Rule-Based Diagnosis Engine for run {run_id} (Provider: {provider})")
            return baseline_incident

        # Query factual context
        run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        logs = db.query(ExecutionLog).filter(ExecutionLog.run_id == run_id).order_by(ExecutionLog.timestamp).all()
        qcs = db.query(QualityCheckResult).filter(QualityCheckResult.run_id == run_id).all()

        factual_context = {
            "pipeline_id": run.pipeline_id if run else "",
            "scenario": run.scenario if run else "",
            "status": run.status if run else "",
            "source_record_count": run.source_record_count if run else 0,
            "target_record_count": run.target_record_count if run else 0,
            "error_message": run.error_message if run else "",
            "execution_logs": [
                {"timestamp": l.timestamp.isoformat(), "level": l.level, "stage": l.stage, "message": l.message}
                for l in logs[-15:]
            ],
            "quality_checks": [
                {
                    "name": q.check_name,
                    "type": q.check_type,
                    "status": q.status,
                    "severity": q.severity,
                    "details": json.loads(q.details_json) if q.details_json else {},
                }
                for q in qcs
            ],
            "deterministic_rule_findings": {
                "category": baseline_incident.category,
                "evidence": json.loads(baseline_incident.evidence_json) if baseline_incident.evidence_json else {},
            },
        }

        # Attempt AI enhancement with strict grounded prompt
        try:
            enhanced_summary = cls._call_ai_provider(provider, api_key, factual_context)
            if enhanced_summary:
                baseline_incident.root_cause_summary = enhanced_summary.get(
                    "root_cause_summary", baseline_incident.root_cause_summary
                )
                baseline_incident.recommendation = enhanced_summary.get(
                    "recommendation", baseline_incident.recommendation
                )
                baseline_incident.confidence_score = float(
                    enhanced_summary.get("confidence_score", baseline_incident.confidence_score)
                )
                db.commit()
                db.refresh(baseline_incident)
                logger.info(f"Enhanced incident {baseline_incident.id} using AI provider: {provider}")
        except Exception as e:
            logger.warning(f"AI Provider ({provider}) call failed or timed out: {e}. Preserving rule-based diagnosis.")

        return baseline_incident

    @classmethod
    def _call_ai_provider(
        cls, provider: str, api_key: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        prompt = (
            "You are an expert Data Engineering Reliability AI. Analyze the following verified pipeline execution facts. "
            "Never hallucinate or claim causes not substantiated by the provided logs and quality checks.\n\n"
            f"Pipeline Execution Evidence:\n{json.dumps(context, indent=2)}\n\n"
            "Return a JSON object with exactly these keys:\n"
            "{\n"
            '  "root_cause_summary": "Crisp 1-2 sentence factual explanation of why the pipeline failed",\n'
            '  "recommendation": "Step-by-step actionable resolution recommendation",\n'
            '  "confidence_score": 0.98\n'
            "}"
        )

        if provider == "openai":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": settings.AI_MODEL_NAME or "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a factual Data Pipeline Diagnostic Agent. Output pure JSON."},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    return json.loads(content)

        elif provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    text_out = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text_out)

        return None
