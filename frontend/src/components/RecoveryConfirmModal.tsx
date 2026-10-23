import React, { useState, useEffect } from "react";
import { X, ShieldAlert, CheckCircle2, RefreshCw, AlertTriangle, ArrowRight } from "lucide-react";
import { api } from "../api/client";
import { RecoveryActionPlan, RecoveryAttemptResponse } from "../types";

interface RecoveryConfirmModalProps {
  isOpen: boolean;
  runId: string | null;
  onClose: () => void;
  onComplete?: (result: RecoveryAttemptResponse) => void;
}

export const RecoveryConfirmModal: React.FC<RecoveryConfirmModalProps> = ({
  isOpen,
  runId,
  onClose,
  onComplete,
}) => {
  const [plan, setPlan] = useState<RecoveryActionPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecoveryAttemptResponse | null>(null);

  useEffect(() => {
    if (isOpen && runId) {
      setLoading(true);
      setError(null);
      setResult(null);
      api
        .getRecoveryPlan(runId)
        .then(setPlan)
        .catch((err) => setError(err.message || "Failed to load recovery plan"))
        .finally(() => setLoading(false));
    }
  }, [isOpen, runId]);

  if (!isOpen || !runId) return null;

  const handleExecute = async () => {
    if (!plan) return;
    setExecuting(true);
    setError(null);
    try {
      const res = await api.executeRecovery(runId, true, plan.strategy);
      setResult(res);
      if (onComplete) onComplete(res);
    } catch (err: any) {
      setError(err.message || "Recovery attempt failed");
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/85 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-xl bg-navy-900 border border-navy-700 rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-navy-700/80 flex items-center justify-between bg-navy-850/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center border border-blue-500/30">
              <RefreshCw className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">Recovery Action Confirmation</h3>
              <p className="text-xs text-slate-400">Run ID: <span className="font-mono text-cyan-400">{runId}</span></p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-navy-800 text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {loading && (
            <div className="py-8 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
              <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              <span>Analyzing safety parameters & generating recovery plan...</span>
            </div>
          )}

          {error && (
            <div className="p-3.5 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="p-4 rounded-lg bg-emerald-500/15 border border-emerald-500/30 space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
                <CheckCircle2 className="w-5 h-5" />
                <span>Recovery Execution Completed Successfully!</span>
              </div>
              <p className="text-xs text-slate-300">{result.notes}</p>
              <div className="flex items-center gap-4 text-xs font-mono text-slate-400 pt-1">
                <span>Recovered Records: <strong className="text-emerald-400">{result.records_recovered}</strong></span>
                <span>Strategy: <strong className="text-cyan-400">{result.strategy}</strong></span>
              </div>
            </div>
          )}

          {!loading && plan && !result && (
            <div className="space-y-4">
              {/* Plan Description Card */}
              <div className="p-4 rounded-lg bg-navy-950 border border-navy-700/80 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">Planned Strategy</span>
                  <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-mono text-[11px]">
                    {plan.strategy}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{plan.action_description}</p>
              </div>

              {/* Safety Guarantees */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 text-xs space-y-1">
                  <span className="text-slate-400 text-[11px] block">Duplicate Protection</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Idempotent Upsert Active
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 text-xs space-y-1">
                  <span className="text-slate-400 text-[11px] block">Historical Integrity</span>
                  <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Original Run Preserved
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5 text-amber-400" />
                <span>
                  This operation will re-execute pipeline ingestion logic with sanitization and validation.
                  Existing target rows will not be duplicated.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-navy-700/80 bg-navy-850/60 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-navy-800"
          >
            {result ? "Close" : "Cancel"}
          </button>
          {!result && plan && (
            <button
              onClick={handleExecute}
              disabled={executing || loading}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs shadow-md shadow-blue-500/20 disabled:opacity-50 transition-all"
            >
              {executing ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Executing Safe Recovery...</span>
                </>
              ) : (
                <>
                  <span>Confirm & Execute Recovery</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
