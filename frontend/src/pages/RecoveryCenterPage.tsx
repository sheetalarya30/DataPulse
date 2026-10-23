import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  RefreshCw,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCw,
  ArrowRight,
  Database,
  History,
  Lock,
  Layers,
} from "lucide-react";
import { api } from "../api/client";
import { PipelineRun, Incident } from "../types";
import { RecoveryConfirmModal } from "../components/RecoveryConfirmModal";

export const RecoveryCenterPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const preselectedRunId = searchParams.get("run");

  const [failedRuns, setFailedRuns] = useState<PipelineRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(preselectedRunId);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  // Recovery Modal
  const [recoveryModalOpen, setRecoveryModalOpen] = useState(false);
  const [activeModalRunId, setActiveModalRunId] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getPipelines().then(async (pipes) => {
        const allRuns: PipelineRun[] = [];
        for (const p of pipes) {
          const r = await api.getPipelineRuns(p.id);
          allRuns.push(...r);
        }
        return allRuns.filter((r) => r.status === "failed");
      }),
      api.getIncidents(),
    ])
      .then(([runs, incs]) => {
        setFailedRuns(runs);
        setIncidents(incs);
        if (runs.length > 0 && !selectedRunId) {
          setSelectedRunId(runs[0].id);
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [preselectedRunId]);

  const handleTriggerRecovery = (runId: string) => {
    setActiveModalRunId(runId);
    setRecoveryModalOpen(true);
  };

  const selectedRun = failedRuns.find((r) => r.id === selectedRunId);
  const matchedIncident = incidents.find((i) => i.run_id === selectedRunId);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Recovery Confirmation Modal */}
      <RecoveryConfirmModal
        isOpen={recoveryModalOpen}
        runId={activeModalRunId}
        onClose={() => {
          setRecoveryModalOpen(false);
          setActiveModalRunId(null);
        }}
        onComplete={() => {
          loadData();
        }}
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-cyan-400" /> Safe Recovery & Retry Center
          </h2>
          <p className="text-xs text-slate-400">
            Idempotent recovery orchestration with pre-flight safety verification and duplicate prevention
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white border border-navy-700 transition-colors"
          title="Refresh"
        >
          <RotateCw className="w-4 h-4" />
        </button>
      </div>

      {/* Safety Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-blue-900/30 via-navy-900 to-navy-950 border border-blue-500/30 flex items-start gap-3.5">
        <div className="p-2 rounded-lg bg-blue-500/20 text-cyan-400 border border-blue-500/30 shrink-0">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-bold text-white text-sm">Idempotent Staging-and-Merge Guarantees</h4>
          <p className="text-slate-300 leading-relaxed">
            DataPulse prevents duplicate records during pipeline retries by using unique primary key upserts
            and pre-flight partition validation. The original failed execution run and its complete forensic logs
            are permanently preserved for audit and compliance.
          </p>
        </div>
      </div>

      {loading && (
        <div className="py-16 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <div className="w-7 h-7 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span>Scanning for eligible recovery candidates...</span>
        </div>
      )}

      {/* Main Split Layout: Left = Eligible Runs, Right = Recovery Pre-Flight Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List: Failed Runs Needing Recovery (5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-white tracking-tight">
              Recovery Candidates ({failedRuns.length})
            </h3>
            <span className="text-[11px] text-slate-400">Select run to stage recovery</span>
          </div>

          <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {failedRuns.map((r) => {
              const isSelected = selectedRunId === r.id;
              const inc = incidents.find((i) => i.run_id === r.id);

              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedRunId(r.id)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all space-y-2 ${
                    isSelected
                      ? "bg-navy-800 border-cyan-500 shadow-lg shadow-cyan-500/10"
                      : "bg-navy-950/70 border-navy-800/80 hover:border-navy-700 hover:bg-navy-850"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-slate-200">{r.id}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30 uppercase font-bold">
                      FAILED
                    </span>
                  </div>

                  <div className="text-xs text-slate-300 font-medium">
                    Scenario: <span className="capitalize">{r.scenario.replace("_", " ")}</span>
                  </div>

                  {inc && (
                    <div className="text-[11px] text-amber-300/90 line-clamp-1 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                      <span>{inc.title}</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-1 border-t border-navy-800/60">
                    <span>
                      Target: {r.target_record_count} / {r.source_record_count}
                    </span>
                    <span>{new Date(r.started_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              );
            })}

            {failedRuns.length === 0 && !loading && (
              <div className="py-12 text-center text-xs text-slate-500 space-y-2">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                <p>No failed runs awaiting recovery. All pipelines are healthy!</p>
                <p className="text-[11px] text-slate-600">
                  Use "Execute Demo Scenario" to simulate a pipeline failure.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Inspector: Pre-Flight Safety & Execution Action (7 cols) */}
        <div className="lg:col-span-7 p-6 rounded-2xl glass-panel space-y-5">
          {selectedRun ? (
            <>
              <div className="border-b border-navy-800 pb-4 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-navy-800 text-cyan-400 border border-navy-700 font-bold">
                    Pipeline: {selectedRun.pipeline_id}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">Run: {selectedRun.id}</span>
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight">
                  Recovery Pre-Flight Assessment
                </h3>
              </div>

              {/* Execution Failure Recap */}
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 space-y-1.5">
                <span className="text-xs font-bold text-rose-300 block">Failure Root Cause Telemetry</span>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {selectedRun.error_message || "Quality verification check failure during batch load."}
                </p>
                {matchedIncident && (
                  <p className="text-[11px] text-slate-400 pt-1 font-mono">
                    Incident: {matchedIncident.category} • Confidence: {(matchedIncident.confidence_score * 100).toFixed(0)}%
                  </p>
                )}
              </div>

              {/* Safety Guarantees Checklist */}
              <div className="space-y-2.5">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Pre-Flight Safety Verifications
                </h4>

                <div className="space-y-2">
                  <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 flex items-center justify-between text-xs">
                    <span className="text-slate-300 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Idempotent Upsert Strategy
                    </span>
                    <span className="text-[11px] font-mono text-emerald-400">ENABLED (No duplicate rows)</span>
                  </div>

                  <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 flex items-center justify-between text-xs">
                    <span className="text-slate-300 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Audit Log Preservation
                    </span>
                    <span className="text-[11px] font-mono text-emerald-400">ACTIVE (Preserves original run)</span>
                  </div>

                  <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 flex items-center justify-between text-xs">
                    <span className="text-slate-300 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Post-Recovery Validation
                    </span>
                    <span className="text-[11px] font-mono text-cyan-400">MANDATORY (6 Quality Suites)</span>
                  </div>
                </div>
              </div>

              {/* Launch Recovery Action */}
              <div className="p-5 rounded-xl bg-gradient-to-r from-navy-950 via-navy-900 to-navy-950 border border-navy-700 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="space-y-1 text-center sm:text-left">
                  <span className="font-bold text-sm text-white block">Ready to Recover</span>
                  <p className="text-xs text-slate-400">
                    Re-executes ingestion logic with sanitization and validation.
                  </p>
                </div>

                <button
                  onClick={() => handleTriggerRecovery(selectedRun.id)}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs shadow-lg shadow-blue-500/20 shrink-0 transition-all hover:scale-[1.02]"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Execute Safe Recovery</span>
                </button>
              </div>
            </>
          ) : (
            <div className="py-24 text-center text-slate-500 text-xs">
              Select an eligible failed run from the left to assess recovery safety.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
