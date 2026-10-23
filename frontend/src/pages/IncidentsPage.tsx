import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Search,
  Filter,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { api } from "../api/client";
import { Incident } from "../types";
import { RecoveryConfirmModal } from "../components/RecoveryConfirmModal";

export const IncidentsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const focusedId = searchParams.get("focus");

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);

  // Recovery Modal State
  const [recoveryRunId, setRecoveryRunId] = useState<string | null>(null);

  const loadIncidents = () => {
    setLoading(true);
    const filter = statusFilter === "ALL" ? undefined : statusFilter;
    api
      .getIncidents(filter)
      .then((data) => {
        setIncidents(data);
        if (data.length > 0) {
          const matched = focusedId ? data.find((d) => d.id === focusedId) : data[0];
          setSelectedIncident(matched || data[0]);
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadIncidents();
  }, [statusFilter, focusedId]);

  const handleOpenRecovery = (runId: string) => {
    setRecoveryRunId(runId);
  };

  const handleRecoveryComplete = () => {
    loadIncidents();
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Recovery Modal */}
      <RecoveryConfirmModal
        isOpen={!!recoveryRunId}
        runId={recoveryRunId}
        onClose={() => setRecoveryRunId(null)}
        onComplete={handleRecoveryComplete}
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" /> Forensic Incident Investigation
          </h2>
          <p className="text-xs text-slate-400">
            Factual root-cause analysis, forensic evidence inspection, and recovery recommendations
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 p-1 rounded-lg bg-navy-900 border border-navy-700 text-xs font-medium">
          {["ALL", "UNRESOLVED", "RESOLVED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-md transition-all ${
                statusFilter === st
                  ? "bg-cyan-500/20 text-cyan-400 font-bold border border-cyan-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="py-16 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <div className="w-7 h-7 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span>Analyzing forensic incident logs...</span>
        </div>
      )}

      {/* Main Split Layout: Left = Incident List, Right = Investigation Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List (5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-white tracking-tight">
              Incidents ({incidents.length})
            </h3>
            <span className="text-[11px] text-slate-400">Select incident to investigate</span>
          </div>

          <div className="space-y-2.5 max-h-[650px] overflow-y-auto pr-1">
            {incidents.map((inc) => {
              const isSelected = selectedIncident?.id === inc.id;
              let parsedEv: any = {};
              try {
                parsedEv = JSON.parse(inc.evidence_json);
              } catch {}

              return (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all space-y-2 ${
                    isSelected
                      ? "bg-navy-800 border-cyan-500 shadow-lg shadow-cyan-500/10"
                      : "bg-navy-950/70 border-navy-800/80 hover:border-navy-700 hover:bg-navy-850"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase border ${
                        inc.severity === "CRITICAL"
                          ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                          : inc.severity === "HIGH"
                          ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                          : "bg-blue-500/20 text-blue-400 border-blue-500/30"
                      }`}
                    >
                      {inc.category}
                    </span>
                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                        inc.status === "RESOLVED"
                          ? "text-emerald-400 bg-emerald-500/15"
                          : "text-amber-400 bg-amber-500/15"
                      }`}
                    >
                      {inc.status}
                    </span>
                  </div>

                  <h4 className="font-bold text-xs text-slate-100 line-clamp-1">{inc.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {inc.root_cause_summary}
                  </p>

                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-1 border-t border-navy-800/60">
                    <span>Run: {inc.run_id}</span>
                    <span>Confidence: {(inc.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Detail (7 cols) */}
        <div className="lg:col-span-7 p-6 rounded-2xl glass-panel space-y-5">
          {selectedIncident ? (
            <>
              {/* Header */}
              <div className="flex items-start justify-between gap-4 border-b border-navy-800 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-navy-800 text-cyan-400 border border-navy-700">
                      {selectedIncident.category}
                    </span>
                    <span
                      className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${
                        selectedIncident.status === "RESOLVED"
                          ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                          : "bg-amber-500/20 text-amber-400 border-amber-500/30"
                      }`}
                    >
                      {selectedIncident.status}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      {new Date(selectedIncident.created_at).toLocaleString()}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white tracking-tight">
                    {selectedIncident.title}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">Incident ID: {selectedIncident.id}</p>
                </div>

                {selectedIncident.status !== "RESOLVED" && (
                  <button
                    onClick={() => handleOpenRecovery(selectedIncident.run_id)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs shadow-md shadow-blue-500/20 shrink-0 transition-all hover:scale-[1.02]"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Recover Run Now</span>
                  </button>
                )}
              </div>

              {/* Likely Root Cause Card */}
              <div className="p-4 rounded-xl bg-navy-950 border border-navy-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5 text-cyan-400">
                    <Sparkles className="w-4 h-4" /> Root-Cause Explanation
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    Confidence: <strong className="text-emerald-400">{(selectedIncident.confidence_score * 100).toFixed(0)}%</strong>
                  </span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {selectedIncident.root_cause_summary}
                </p>
              </div>

              {/* Supporting Forensic Evidence */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-cyan-400" /> Supporting Forensic Evidence
                </h4>
                <div className="p-4 rounded-xl bg-navy-950 font-mono text-xs border border-navy-800/80 text-slate-300 space-y-2 max-h-56 overflow-y-auto">
                  <pre className="text-[11px] text-cyan-300/90 whitespace-pre-wrap">
                    {JSON.stringify(JSON.parse(selectedIncident.evidence_json || "{}"), null, 2)}
                  </pre>
                </div>
              </div>

              {/* Recommendation Card */}
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/25 space-y-1.5">
                <span className="text-xs font-bold text-cyan-300 block">Recommended Recovery Strategy</span>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {selectedIncident.recommendation}
                </p>
              </div>

              {/* Links */}
              <div className="flex items-center justify-between pt-2 border-t border-navy-800 text-xs text-slate-400">
                <span>Associated Execution Run:</span>
                <Link
                  to={`/pipelines/${selectedIncident.pipeline_id}?run=${selectedIncident.run_id}`}
                  className="text-cyan-400 hover:text-cyan-300 font-mono font-semibold flex items-center gap-1"
                >
                  View Run Logs & Telemetry <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </>
          ) : (
            <div className="py-24 text-center text-slate-500 text-xs">
              Select an incident from the left to inspect forensic telemetry.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
