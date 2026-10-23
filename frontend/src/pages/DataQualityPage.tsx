import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCw,
  FileCode,
  Table,
  Eye,
  X,
} from "lucide-react";
import { api } from "../api/client";
import { QualitySummaryResponse, QualityCheckItem } from "../types";

export const DataQualityPage: React.FC = () => {
  const [data, setData] = useState<QualitySummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Inspector modal for selected check
  const [inspectedCheck, setInspectedCheck] = useState<QualityCheckItem | null>(null);

  const loadQualityData = () => {
    setLoading(true);
    api
      .getQualitySummary()
      .then(setData)
      .catch((err) => setError(err.message || "Failed to load quality metrics"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQualityData();
  }, []);

  const CHECK_DEFINITIONS = [
    {
      type: "RECONCILIATION",
      title: "Row Count Reconciliation",
      desc: "Compares source extracted count vs target warehouse loaded count to detect silent packet or partition loss.",
    },
    {
      type: "UNIQUENESS",
      title: "Primary Key Uniqueness",
      desc: "Guarantees that order_id and business key columns are strictly unique without duplicate collisions.",
    },
    {
      type: "COMPLETENESS",
      title: "Mandatory Field Completeness",
      desc: "Ensures essential columns (customer_email, amount, order_date) do not contain null or empty values.",
    },
    {
      type: "SCHEMA",
      title: "Schema Drift & Column Conformance",
      desc: "Detects missing mandatory columns, column renamings, and unmapped fields from upstream sources.",
    },
    {
      type: "FORMAT",
      title: "Syntax & Boundary Validation",
      desc: "Coerces ISO timestamps, verifies email regex compliance, and asserts non-negative numeric amounts.",
    },
    {
      type: "VOLUME",
      title: "Batch Volume Anomaly Detection",
      desc: "Monitors ingestion throughput to flag anomalous volume drops or unexpected surges.",
    },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Evidence Inspector Modal */}
      {inspectedCheck && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-xl bg-navy-900 border border-navy-700 rounded-xl shadow-2xl overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-navy-700/80 flex items-center justify-between bg-navy-850/60">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">{inspectedCheck.check_name}</h3>
                <p className="text-xs text-slate-400 font-mono">Run: {inspectedCheck.run_id}</p>
              </div>
              <button
                onClick={() => setInspectedCheck(null)}
                className="p-1 rounded-lg hover:bg-navy-800 text-slate-400 hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-3 gap-2 text-xs font-mono text-center">
                <div className="p-2 rounded bg-navy-950 border border-navy-800">
                  <span className="text-slate-500 text-[10px] block">Status</span>
                  <span className={inspectedCheck.status === "PASSED" ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                    {inspectedCheck.status}
                  </span>
                </div>
                <div className="p-2 rounded bg-navy-950 border border-navy-800">
                  <span className="text-slate-500 text-[10px] block">Evaluated</span>
                  <span className="text-slate-200 font-bold">{inspectedCheck.records_evaluated}</span>
                </div>
                <div className="p-2 rounded bg-navy-950 border border-navy-800">
                  <span className="text-slate-500 text-[10px] block">Failed Rows</span>
                  <span className="text-rose-400 font-bold">{inspectedCheck.records_failed}</span>
                </div>
              </div>

              <div>
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-1">
                  Structured Evidence Details
                </span>
                <pre className="p-4 rounded-xl bg-navy-950 font-mono text-xs text-cyan-300 border border-navy-800 overflow-x-auto max-h-60">
                  {inspectedCheck.details_json}
                </pre>
              </div>
            </div>
            <div className="px-6 py-3 border-t border-navy-700/80 bg-navy-850/60 text-right">
              <button
                onClick={() => setInspectedCheck(null)}
                className="px-4 py-1.5 rounded-lg text-xs font-medium bg-navy-800 text-slate-300 hover:text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-cyan-400" /> Automated Data Quality Guardrails
          </h2>
          <p className="text-xs text-slate-400">
            Real-time validation suites protecting analytics tables from incomplete or malformed loads
          </p>
        </div>
        <button
          onClick={loadQualityData}
          className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white border border-navy-700 transition-colors"
          title="Refresh quality metrics"
        >
          <RotateCw className="w-4 h-4" />
        </button>
      </div>

      {loading && !data && (
        <div className="py-16 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <div className="w-7 h-7 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span>Aggregating quality test suites...</span>
        </div>
      )}

      {data && (
        <>
          {/* Top Score Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl glass-panel">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-1">
                Quality Compliance Rate
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-white tracking-tight">{data.pass_rate}%</span>
                <span className="text-xs text-emerald-400 font-medium">all check suites</span>
              </div>
              <div className="mt-3 w-full bg-navy-950 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-1.5 rounded-full"
                  style={{ width: `${data.pass_rate}%` }}
                />
              </div>
            </div>

            <div className="p-4 rounded-xl glass-panel">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-1">
                Total Check Executions
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-white tracking-tight">{data.total_checks}</span>
                <span className="text-xs text-slate-400">assertions evaluated</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-3 block font-mono">
                {data.passed_checks} passed tests across runs
              </span>
            </div>

            <div className="p-4 rounded-xl glass-panel">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-1">
                Total Violations Detected
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-rose-400 tracking-tight">
                  {data.failed_checks + data.warning_checks}
                </span>
                <span className="text-xs text-rose-300">anomalies flagged</span>
              </div>
              <span className="text-[11px] text-slate-500 mt-3 block font-mono">
                {data.failed_checks} failed • {data.warning_checks} warnings
              </span>
            </div>
          </div>

          {/* 6 Core Check Types Grid */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white tracking-tight">Standard Quality Validation Suites</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {CHECK_DEFINITIONS.map((def) => {
                const stats = data.checks_by_type[def.type] || { PASSED: 0, FAILED: 0, WARNING: 0, TOTAL: 0 };
                const passRatio = stats.TOTAL > 0 ? ((stats.PASSED / stats.TOTAL) * 100).toFixed(0) : "100";

                return (
                  <div key={def.type} className="p-4 rounded-xl glass-panel glass-panel-hover space-y-3 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-navy-800 text-cyan-400 border border-navy-700 font-bold">
                          {def.type}
                        </span>
                        <span className="text-xs font-mono font-bold text-slate-300">
                          {passRatio}% Pass
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-slate-100">{def.title}</h4>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">{def.desc}</p>
                    </div>

                    <div className="pt-2 border-t border-navy-800/80 flex items-center justify-between text-xs font-mono">
                      <span className="text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> {stats.PASSED} Pass
                      </span>
                      <span className="text-rose-400 flex items-center gap-1">
                        <XCircle className="w-3.5 h-3.5" /> {stats.FAILED} Fail
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Quality Failures Table */}
          <div className="p-5 rounded-2xl glass-panel space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-400" /> Recent Failed Quality Checks & Evidence
                </h3>
                <p className="text-xs text-slate-400">Detailed records of recent rule violations</p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-navy-800">
                  <tr>
                    <th className="pb-2.5 font-semibold">Check Name</th>
                    <th className="pb-2.5 font-semibold">Type</th>
                    <th className="pb-2.5 font-semibold">Status</th>
                    <th className="pb-2.5 font-semibold">Run ID</th>
                    <th className="pb-2.5 font-semibold">Failed Rows</th>
                    <th className="pb-2.5 font-semibold">Timestamp</th>
                    <th className="pb-2.5 font-semibold text-right">Evidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-navy-800/60 font-mono">
                  {data.recent_failures && data.recent_failures.length > 0 ? (
                    data.recent_failures.map((qc) => (
                      <tr key={qc.id} className="hover:bg-navy-850/50">
                        <td className="py-3 pr-2 text-slate-200 font-sans font-medium">{qc.check_name}</td>
                        <td className="py-3 pr-2 text-cyan-400">{qc.check_type}</td>
                        <td className="py-3 pr-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/15 text-rose-400 border border-rose-500/30">
                            {qc.status}
                          </span>
                        </td>
                        <td className="py-3 pr-2 text-slate-400">{qc.run_id}</td>
                        <td className="py-3 pr-2 font-bold text-rose-400">{qc.records_failed}</td>
                        <td className="py-3 pr-2 text-slate-500 text-[11px]">
                          {new Date(qc.created_at).toLocaleTimeString()}
                        </td>
                        <td className="py-3 text-right">
                          <button
                            onClick={() => setInspectedCheck(qc)}
                            className="p-1 rounded bg-navy-800 hover:bg-navy-700 text-cyan-400 hover:text-cyan-300 border border-navy-700"
                            title="Inspect structured evidence"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500">
                        No recent quality failures.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
