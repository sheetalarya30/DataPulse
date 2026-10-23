import React, { useState, useEffect } from "react";
import { useParams, Link, useSearchParams } from "react-router-dom";
import {
  GitBranch,
  ArrowLeft,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Terminal,
  ShieldCheck,
  AlertTriangle,
  RotateCw,
  Search,
  ChevronRight,
  Database,
  Filter,
} from "lucide-react";
import { api } from "../api/client";
import { Pipeline, PipelineRun, ExecutionLog, QualityCheckItem } from "../types";

interface PipelineDetailPageProps {
  onOpenTriggerModal: () => void;
}

export const PipelineDetailPage: React.FC<PipelineDetailPageProps> = ({ onOpenTriggerModal }) => {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const initialRunId = searchParams.get("run");

  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(initialRunId);
  const [selectedRun, setSelectedRun] = useState<PipelineRun | null>(null);

  const [activeTab, setActiveTab] = useState<"logs" | "quality" | "overview">("logs");
  const [logFilter, setLogFilter] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      setLoading(true);
      Promise.all([api.getPipeline(id), api.getPipelineRuns(id)])
        .then(([pipeData, runsData]) => {
          setPipeline(pipeData);
          setRuns(runsData);
          if (runsData.length > 0) {
            const targetRunId = initialRunId || runsData[0].id;
            setSelectedRunId(targetRunId);
          }
        })
        .finally(() => setLoading(false));
    }
  }, [id, initialRunId]);

  useEffect(() => {
    if (selectedRunId) {
      api.getRun(selectedRunId).then(setSelectedRun).catch(console.error);
    }
  }, [selectedRunId]);

  if (loading && !pipeline) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-slate-400">Loading pipeline execution history...</span>
      </div>
    );
  }

  if (!pipeline) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Pipeline not found.</p>
        <Link to="/pipelines" className="text-cyan-400 underline mt-2 block">
          Back to Pipelines
        </Link>
      </div>
    );
  }

  const filteredLogs = selectedRun?.logs?.filter((l) => {
    if (logFilter === "ALL") return true;
    return l.level === logFilter;
  });

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/pipelines"
            className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-400 hover:text-white border border-navy-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 uppercase font-semibold">
                {pipeline.code}
              </span>
              <span className="text-xs text-slate-400">ID: {pipeline.id}</span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">{pipeline.name}</h2>
          </div>
        </div>

        <button
          onClick={onOpenTriggerModal}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 transition-all hover:scale-[1.02]"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Execute Demo Scenario</span>
        </button>
      </div>

      {/* Pipeline Config Specs */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 p-4 rounded-xl glass-panel text-xs">
        <div>
          <span className="text-slate-500 text-[11px] block">Source Definition</span>
          <span className="text-slate-200 font-semibold font-mono">{pipeline.source_type}</span>
        </div>
        <div>
          <span className="text-slate-500 text-[11px] block">Target Warehouse</span>
          <span className="text-cyan-400 font-semibold font-mono">{pipeline.target_type}</span>
        </div>
        <div>
          <span className="text-slate-500 text-[11px] block">Trigger Cadence</span>
          <span className="text-slate-200 font-mono">{pipeline.schedule}</span>
        </div>
        <div>
          <span className="text-slate-500 text-[11px] block">Lifetime Success Ratio</span>
          <span className="text-emerald-400 font-bold font-mono">{pipeline.success_rate}%</span>
        </div>
      </div>

      {/* Main Split Layout: Left = Runs List, Right = Run Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Runs Table (5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-white tracking-tight flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" /> Execution History ({runs.length})
            </h3>
            <span className="text-[11px] text-slate-400">Select run to inspect</span>
          </div>

          <div className="space-y-2 max-h-[650px] overflow-y-auto pr-1">
            {runs.map((r) => {
              const isSelected = selectedRunId === r.id;
              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedRunId(r.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-navy-800 border-cyan-500 shadow-lg shadow-cyan-500/10"
                      : "bg-navy-950/60 border-navy-800/80 hover:border-navy-700 hover:bg-navy-850/60"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-semibold text-slate-200">{r.id}</span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        r.status === "success"
                          ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                          : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                      }`}
                    >
                      {r.status === "success" ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <XCircle className="w-3 h-3" />
                      )}
                      {r.status}
                    </span>
                  </div>

                  <div className="text-[11px] text-slate-400 flex items-center justify-between">
                    <span className="capitalize">Scenario: {r.scenario.replace("_", " ")}</span>
                    <span className="font-mono">{(r.duration_ms / 1000).toFixed(2)}s</span>
                  </div>

                  <div className="text-[10px] text-slate-500 font-mono mt-1 pt-1 border-t border-navy-800/60 flex items-center justify-between">
                    <span>
                      Recs: {r.target_record_count} / {r.source_record_count}
                    </span>
                    {r.is_retry && <span className="text-cyan-400 font-bold uppercase">[RETRY]</span>}
                    <span>{new Date(r.started_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Selected Run Inspector (7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-2xl glass-panel space-y-4 flex flex-col">
          {selectedRun ? (
            <>
              {/* Header with Run Metadata */}
              <div className="p-4 rounded-xl bg-navy-950/80 border border-navy-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-white">{selectedRun.id}</span>
                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                        selectedRun.status === "success"
                          ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                          : "bg-rose-500/20 text-rose-400 border-rose-500/30"
                      }`}
                    >
                      {selectedRun.status}
                    </span>
                    {selectedRun.is_retry && (
                      <span className="text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded font-mono uppercase font-bold">
                        Recovery Run
                      </span>
                    )}
                  </div>

                  {selectedRun.status === "failed" && (
                    <Link
                      to={`/recovery?run=${selectedRun.id}`}
                      className="px-3 py-1 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-xs font-bold shadow-md shadow-blue-500/20 flex items-center gap-1.5 transition-all"
                    >
                      <span>Recover Run</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  )}
                </div>

                <div className="grid grid-cols-4 gap-2 text-center text-xs font-mono pt-1">
                  <div className="p-2 rounded bg-navy-900 border border-navy-800">
                    <span className="text-[10px] text-slate-500 block">Source Recs</span>
                    <span className="font-bold text-slate-200">{selectedRun.source_record_count}</span>
                  </div>
                  <div className="p-2 rounded bg-navy-900 border border-navy-800">
                    <span className="text-[10px] text-slate-500 block">Target Recs</span>
                    <span className="font-bold text-cyan-400">{selectedRun.target_record_count}</span>
                  </div>
                  <div className="p-2 rounded bg-navy-900 border border-navy-800">
                    <span className="text-[10px] text-slate-500 block">Inserted</span>
                    <span className="font-bold text-emerald-400">{selectedRun.records_inserted}</span>
                  </div>
                  <div className="p-2 rounded bg-navy-900 border border-navy-800">
                    <span className="text-[10px] text-slate-500 block">Duration</span>
                    <span className="font-bold text-slate-300">
                      {(selectedRun.duration_ms / 1000).toFixed(2)}s
                    </span>
                  </div>
                </div>

                {selectedRun.error_message && (
                  <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs">
                    <strong className="font-semibold block mb-0.5">Execution Alert:</strong>
                    <span>{selectedRun.error_message}</span>
                  </div>
                )}
              </div>

              {/* Navigation Tabs */}
              <div className="flex items-center justify-between border-b border-navy-800 pb-2">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setActiveTab("logs")}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      activeTab === "logs"
                        ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <Terminal className="w-3.5 h-3.5" />
                    <span>Execution Logs ({selectedRun.logs?.length || 0})</span>
                  </button>

                  <button
                    onClick={() => setActiveTab("quality")}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      activeTab === "quality"
                        ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Quality Checks ({selectedRun.quality_checks?.length || 0})</span>
                  </button>
                </div>

                {activeTab === "logs" && (
                  <div className="flex items-center gap-1 text-[11px] font-mono">
                    <Filter className="w-3 h-3 text-slate-500" />
                    {["ALL", "INFO", "WARNING", "ERROR"].map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => setLogFilter(lvl)}
                        className={`px-2 py-0.5 rounded ${
                          logFilter === lvl
                            ? "bg-navy-800 text-cyan-400 font-bold border border-navy-700"
                            : "text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Tab 1: Execution Logs Viewer */}
              {activeTab === "logs" && (
                <div className="p-4 rounded-xl bg-navy-950 font-mono text-xs border border-navy-800/80 space-y-2 max-h-[460px] overflow-y-auto">
                  {filteredLogs && filteredLogs.length > 0 ? (
                    filteredLogs.map((log) => (
                      <div
                        key={log.id}
                        className={`p-2 rounded text-[11px] leading-relaxed border ${
                          log.level === "ERROR" || log.level === "CRITICAL"
                            ? "bg-rose-500/10 border-rose-500/20 text-rose-300"
                            : log.level === "WARNING"
                            ? "bg-amber-500/10 border-amber-500/20 text-amber-300"
                            : "bg-navy-900/60 border-navy-800/60 text-slate-300"
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                          <span className="text-cyan-400 font-bold">[{log.stage}]</span>
                          <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <p>{log.message}</p>
                        {log.context_data && log.context_data !== "{}" && (
                          <pre className="mt-1 text-[10px] text-slate-400 bg-navy-950/80 p-1.5 rounded overflow-x-auto">
                            {log.context_data}
                          </pre>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="py-8 text-center text-slate-500">No logs for this filter.</div>
                  )}
                </div>
              )}

              {/* Tab 2: Quality Checks Results */}
              {activeTab === "quality" && (
                <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
                  {selectedRun.quality_checks && selectedRun.quality_checks.length > 0 ? (
                    selectedRun.quality_checks.map((qc: any) => (
                      <div
                        key={qc.id}
                        className="p-3.5 rounded-xl bg-navy-950/80 border border-navy-800/80 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-xs text-slate-200">{qc.check_name}</span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              qc.status === "PASSED"
                                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                            }`}
                          >
                            {qc.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono">
                          <span>Type: <strong className="text-cyan-400">{qc.check_type}</strong></span>
                          <span>Failed Recs: <strong className={qc.records_failed > 0 ? "text-rose-400" : "text-emerald-400"}>{qc.records_failed}</strong></span>
                          <span>Time: {qc.execution_time_ms}ms</span>
                        </div>
                        {qc.details && Object.keys(qc.details).length > 0 && (
                          <pre className="text-[10px] font-mono bg-navy-900 p-2 rounded border border-navy-800 text-slate-300 overflow-x-auto">
                            {JSON.stringify(qc.details, null, 2)}
                          </pre>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="py-8 text-center text-slate-500 text-xs">
                      No quality checks evaluated for this run.
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="py-24 text-center text-slate-500 text-xs">Select a run to view logs and validation details.</div>
          )}
        </div>
      </div>
    </div>
  );
};
