import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  ArrowUpRight,
  ShieldCheck,
  Play,
  RotateCw,
  Sparkles,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { api } from "../api/client";
import { DashboardSummary } from "../types";

interface OverviewPageProps {
  onOpenTriggerModal: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onOpenTriggerModal }) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    api
      .getDashboardSummary()
      .then(setData)
      .catch((err) => setError(err.message || "Failed to load dashboard metrics"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading && !data) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-slate-400">Loading live pipeline metrics from database...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 space-y-2">
          <div className="flex items-center gap-2 font-bold text-base">
            <AlertTriangle className="w-5 h-5" />
            <span>Failed to Load Dashboard Data</span>
          </div>
          <p className="text-sm">{error || "Unknown error occurred"}</p>
          <button
            onClick={loadData}
            className="mt-2 px-4 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-xs font-semibold"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const {
    total_pipeline_runs,
    successful_runs,
    failed_runs,
    success_rate,
    avg_duration_ms,
    unresolved_incidents,
    recent_runs,
    active_incidents,
    failure_trends,
    quality_summary,
  } = data;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Action Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl glass-panel bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900 border border-navy-700/80 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold tracking-wider">
              Real-Time Platform
            </span>
            <span className="text-xs text-slate-400">Deterministic Monitoring & Recovery</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Data Pipeline Observability & Safe Recovery
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
            DataPulse continuously reconciles source vs target records, catches silent data anomalies,
            and enables verified idempotent recovery with complete audit preservation.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={loadData}
            className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white border border-navy-700 transition-colors"
            title="Refresh metrics"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          <button
            onClick={onOpenTriggerModal}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs tracking-wide shadow-md shadow-cyan-500/20 transition-all hover:scale-[1.02]"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Launch Test Scenario</span>
          </button>
        </div>
      </div>

      {/* 4 Core Top Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Runs */}
        <div className="p-4 rounded-xl glass-panel glass-panel-hover">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Pipeline Runs</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">{total_pipeline_runs}</span>
            <span className="text-xs text-slate-400">executions recorded</span>
          </div>
          <div className="mt-3 flex items-center gap-3 text-[11px] text-slate-400 border-t border-navy-800/80 pt-2 font-mono">
            <span className="flex items-center gap-1 text-emerald-400">
              <CheckCircle2 className="w-3 h-3" /> {successful_runs} succ
            </span>
            <span className="flex items-center gap-1 text-rose-400">
              <XCircle className="w-3 h-3" /> {failed_runs} fail
            </span>
          </div>
        </div>

        {/* Success Rate */}
        <div className="p-4 rounded-xl glass-panel glass-panel-hover">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Pipeline Success Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">{success_rate}%</span>
            <span className="text-xs text-slate-400">healthy load ratio</span>
          </div>
          {/* Progress bar */}
          <div className="mt-3 w-full bg-navy-950 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(success_rate, 100)}%` }}
            />
          </div>
        </div>

        {/* Average Duration */}
        <div className="p-4 rounded-xl glass-panel glass-panel-hover">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg Processing Duration</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">
              {(avg_duration_ms / 1000).toFixed(2)}s
            </span>
            <span className="text-xs text-slate-400">({avg_duration_ms} ms)</span>
          </div>
          <div className="mt-3 text-[11px] text-slate-400 border-t border-navy-800/80 pt-2 font-mono">
            <span>Aggregated from live telemetry</span>
          </div>
        </div>

        {/* Unresolved Incidents */}
        <div className="p-4 rounded-xl glass-panel glass-panel-hover">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Unresolved Incidents</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">{unresolved_incidents}</span>
            <span className="text-xs text-slate-400">requiring investigation</span>
          </div>
          <div className="mt-3 flex items-center justify-between text-[11px] border-t border-navy-800/80 pt-2">
            <span className="text-slate-400">Status: Action Needed</span>
            <Link to="/incidents" className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-0.5">
              Review <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>

      {/* Middle Section: Failure Trends Chart & Quality Scorecard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Failure Trends Chart (2 cols) */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">Execution & Failure Trends Over Time</h3>
              <p className="text-xs text-slate-400">Historical daily throughput and success rates</p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
              <span className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Total Runs
              </span>
              <span className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-400" /> Failures
              </span>
            </div>
          </div>

          <div className="h-64 w-full pt-2">
            {failure_trends && failure_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={failure_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2c4f" vertical={false} />
                  <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0b1120",
                      borderColor: "#1e293b",
                      borderRadius: "8px",
                      color: "#f8fafc",
                      fontSize: "12px",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="total_runs"
                    stroke="#06b6d4"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorTotal)"
                  />
                  <Area
                    type="monotone"
                    dataKey="failed_runs"
                    stroke="#f43f5e"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorFailed)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No historical trend points recorded yet.
              </div>
            )}
          </div>
        </div>

        {/* Data Quality Overview Card (1 col) */}
        <div className="p-5 rounded-2xl glass-panel space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-cyan-400" /> Data Quality Guardrails
              </h3>
              <Link to="/quality" className="text-xs text-cyan-400 hover:text-cyan-300 font-medium">
                View All
              </Link>
            </div>
            <p className="text-xs text-slate-400">Automated post-load schema & integrity tests</p>

            <div className="mt-5 p-4 rounded-xl bg-navy-950/70 border border-navy-800 text-center">
              <span className="text-3xl font-extrabold text-white tracking-tight">
                {quality_summary.pass_rate}%
              </span>
              <span className="block text-xs text-slate-400 mt-1 font-medium">
                Overall Quality Compliance Rate
              </span>
            </div>

            <div className="mt-4 space-y-2 text-xs">
              <div className="flex items-center justify-between py-1.5 border-b border-navy-800/80">
                <span className="text-slate-400">Total Check Suites Evaluated</span>
                <span className="font-mono font-bold text-slate-200">{quality_summary.total_checks}</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-navy-800/80">
                <span className="text-slate-400">Passed Check Rules</span>
                <span className="font-mono font-bold text-emerald-400">{quality_summary.passed_checks}</span>
              </div>
              <div className="flex items-center justify-between py-1.5">
                <span className="text-slate-400">Failed / Warning Checks</span>
                <span className="font-mono font-bold text-rose-400">{quality_summary.failed_checks}</span>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-[11px] text-cyan-300 flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              Quality checks monitor Row Reconciliation, PK Uniqueness, Field Completeness,
              and Upstream Schema Drift.
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Section: Active Incidents & Recent Pipeline Executions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Incidents */}
        <div className="p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Active Detected Incidents
              </h3>
              <p className="text-xs text-slate-400">Recent pipeline regressions awaiting resolution</p>
            </div>
            <Link to="/incidents" className="text-xs text-cyan-400 hover:text-cyan-300 font-medium">
              Explore All ({unresolved_incidents})
            </Link>
          </div>

          <div className="space-y-2.5">
            {active_incidents && active_incidents.length > 0 ? (
              active_incidents.map((inc) => (
                <div
                  key={inc.id}
                  className="p-3.5 rounded-xl bg-navy-950/80 border border-navy-800 hover:border-navy-700 transition-all space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-slate-200 line-clamp-1">{inc.title}</span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold ${
                        inc.severity === "CRITICAL"
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                      }`}
                    >
                      {inc.category}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {inc.root_cause_summary}
                  </p>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                    <span>Confidence: {(inc.confidence_score * 100).toFixed(0)}%</span>
                    <Link
                      to={`/incidents?focus=${inc.id}`}
                      className="text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
                    >
                      Investigate <ArrowUpRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-8 text-center text-xs text-slate-500">
                No active unresolved incidents. All pipelines are operating nominally!
              </div>
            )}
          </div>
        </div>

        {/* Recent Pipeline Executions */}
        <div className="p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
                <Activity className="w-4 h-4 text-cyan-400" /> Recent Pipeline Executions
              </h3>
              <p className="text-xs text-slate-400">Latest executed batches and outcomes</p>
            </div>
            <Link to="/pipelines" className="text-xs text-cyan-400 hover:text-cyan-300 font-medium">
              View Pipelines
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-navy-800">
                <tr>
                  <th className="pb-2 font-semibold">Run ID / Scenario</th>
                  <th className="pb-2 font-semibold">Status</th>
                  <th className="pb-2 font-semibold">Records</th>
                  <th className="pb-2 font-semibold">Duration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60 font-mono">
                {recent_runs && recent_runs.slice(0, 6).map((run) => (
                  <tr key={run.id} className="hover:bg-navy-850/40">
                    <td className="py-2.5 pr-2">
                      <Link
                        to={`/pipelines/${run.pipeline_id}?run=${run.id}`}
                        className="text-slate-200 hover:text-cyan-400 font-medium block"
                      >
                        {run.id}
                      </Link>
                      <span className="text-[10px] text-slate-500 capitalize block">
                        Scenario: {run.scenario.replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-2.5 pr-2">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          run.status === "success"
                            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {run.status === "success" ? (
                          <CheckCircle2 className="w-2.5 h-2.5" />
                        ) : (
                          <XCircle className="w-2.5 h-2.5" />
                        )}
                        {run.status}
                      </span>
                    </td>
                    <td className="py-2.5 pr-2 text-slate-300">
                      {run.target_record_count} / {run.source_record_count}
                    </td>
                    <td className="py-2.5 text-slate-400">
                      {(run.duration_ms / 1000).toFixed(2)}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
