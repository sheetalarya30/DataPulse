import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.incident import IncidentResponse, IncidentDetailResponse
from app.crud.crud_incident import (
    get_incidents,
    get_incident,
    get_incident_recovery_attempts,
)
from app.core.exceptions import EntityNotFoundError

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentResponse])
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (e.g. UNRESOLVED, RESOLVED)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve all detected pipeline incidents."""
    return get_incidents(db, status=status, skip=skip, limit=limit)


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident_detail(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve deep forensic investigation details for an incident."""
    incident = get_incident(db, incident_id)
    if not incident:
        raise EntityNotFoundError("Incident", incident_id)

    try:
        parsed_evidence = json.loads(incident.evidence_json) if incident.evidence_json else {}
    except Exception:
        parsed_evidence = {}

    recovery_attempts = get_incident_recovery_attempts(db, incident_id)
    formatted_recovery = [
        {
            "id": rec.id,
            "strategy": rec.strategy,
            "status": rec.status,
            "records_recovered": rec.records_recovered,
            "validation_passed": rec.validation_passed,
            "notes": rec.notes,
            "created_at": rec.created_at.isoformat(),
        }
        for rec in recovery_attempts
    ]

    return IncidentDetailResponse(
        id=incident.id,
        run_id=incident.run_id,
        pipeline_id=incident.pipeline_id,
        pipeline_name=incident.pipeline.name if incident.pipeline else None,
        pipeline_code=incident.pipeline.code if incident.pipeline else None,
        run_status=incident.run.status if incident.run else None,
        run_scenario=incident.run.scenario if incident.run else None,
        title=incident.title,
        category=incident.category,
        severity=incident.severity,
        status=incident.status,
        root_cause_summary=incident.root_cause_summary,
        confidence_score=incident.confidence_score,
        evidence_json=incident.evidence_json,
        parsed_evidence=parsed_evidence,
        recommendation=incident.recommendation,
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        recovery_attempts=formatted_recovery,
    )
