import React, { useState } from "react";
import { X, Play, AlertCircle, CheckCircle2, ChevronRight, Zap } from "lucide-react";
import { api } from "../api/client";
import { PipelineRun } from "../types";

interface TriggerRunModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (newRun: PipelineRun) => void;
}

const SCENARIOS = [
  {
    id: "success",
    name: "1. Successful Execution",
    badge: "Clean Run",
    badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    desc: "Ingests 50 valid e-commerce orders. All 6 quality check suites pass with 100% compliance.",
  },
  {
    id: "missing_records",
    name: "2. Incomplete Load (Record Loss)",
    badge: "Reconciliation Deficit",
    badgeColor: "bg-rose-500/20 text-rose-400 border-rose-500/30",
    desc: "Simulates worker dropout omitting 10 rows during transformation. Triggers reconciliation check failure and RECORD_LOSS incident.",
  },
  {
    id: "duplicate_orders",
    name: "3. Duplicate Order IDs",
    badge: "Uniqueness Collision",
    badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    desc: "Injects 5 duplicate order_id records. Caught by primary key uniqueness checks before warehouse corruption.",
  },
  {
    id: "null_values",
    name: "4. Null Required Fields",
    badge: "Completeness Violation",
    badgeColor: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    desc: "Injects missing customer_email and order amount fields. Flags completeness quality check failures.",
  },
  {
    id: "invalid_formats",
    name: "5. Invalid Formats & Boundary",
    badge: "Syntax Error",
    badgeColor: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    desc: "Injects corrupt timestamps and negative financial amounts. Flags format validation errors.",
  },
  {
    id: "schema_mismatch",
    name: "6. Upstream Schema Drift",
    badge: "Schema Mismatch",
    badgeColor: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    desc: "Source schema renames order_id to order_tracking_num. Aborts in pre-load validation.",
  },
  {
    id: "pipeline_failure",
    name: "7. Fatal System Crash",
    badge: "Connection Error",
    badgeColor: "bg-red-500/20 text-red-400 border-red-500/30",
    desc: "Simulates database connection reset by peer during LOAD stage. Tests crash diagnostics and state preservation.",
  },
];

export const TriggerRunModal: React.FC<TriggerRunModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [selectedScenario, setSelectedScenario] = useState("success");
  const [pipelineId, setPipelineId] = useState("pipe-ecommerce-orders");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const run = await api.triggerPipelineRun(pipelineId, selectedScenario);
      if (onSuccess) onSuccess(run);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to trigger execution");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-navy-900 border border-navy-700 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-navy-700/80 flex items-center justify-between bg-navy-850/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">Execute Demo Scenario</h3>
              <p className="text-xs text-slate-400">Trigger deterministic data pipeline test scenarios</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-navy-800 text-slate-400 hover:text-slate-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 overflow-y-auto">
          {error && (
            <div className="p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Target Pipeline
            </label>
            <select
              value={pipelineId}
              onChange={(e) => setPipelineId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-navy-950 border border-navy-700 text-slate-200 text-sm focus:outline-none focus:border-cyan-500"
            >
              <option value="pipe-ecommerce-orders">E-Commerce Orders Ingestion & Cleansing</option>
              <option value="pipe-inventory-sync">Warehouse Inventory & Stock Synchronizer</option>
              <option value="pipe-clickstream-events">Website Clickstream Event Processor</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Select Execution Scenario
            </label>
            <div className="space-y-2">
              {SCENARIOS.map((sc) => {
                const isSelected = selectedScenario === sc.id;
                return (
                  <div
                    key={sc.id}
                    onClick={() => setSelectedScenario(sc.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? "bg-navy-800/90 border-cyan-500 shadow-md shadow-cyan-500/10"
                        : "bg-navy-950/60 border-navy-800 hover:border-navy-700 hover:bg-navy-850"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-slate-200">{sc.name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded border ${sc.badgeColor}`}>
                          {sc.badge}
                        </span>
                      </div>
                      <input
                        type="radio"
                        checked={isSelected}
                        onChange={() => setSelectedScenario(sc.id)}
                        className="accent-cyan-400"
                      />
                    </div>
                    <p className="text-xs text-slate-400 pl-0.5">{sc.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-navy-700/80 bg-navy-850/60 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-navy-800"
          >
            Cancel
          </button>
          <button
            onClick={handleRun}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 disabled:opacity-50 transition-all"
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Running Pipeline Logic...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Launch Scenario</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
