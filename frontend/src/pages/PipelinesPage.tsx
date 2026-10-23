import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  GitBranch,
  Play,
  Clock,
  CheckCircle2,
  XCircle,
  Database,
  ArrowRight,
  RotateCw,
  ExternalLink,
  Layers,
} from "lucide-react";
import { api } from "../api/client";
import { Pipeline } from "../types";

interface PipelinesPageProps {
  onOpenTriggerModal: () => void;
}

export const PipelinesPage: React.FC<PipelinesPageProps> = ({ onOpenTriggerModal }) => {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPipelines = () => {
    setLoading(true);
    api
      .getPipelines()
      .then(setPipelines)
      .catch((err) => setError(err.message || "Failed to load pipelines"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPipelines();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-cyan-400" /> Registered Data Pipelines
          </h2>
          <p className="text-xs text-slate-400">
            Monitor and execute ETL data pipelines across cloud and warehouse storage
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadPipelines}
            className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white border border-navy-700 transition-colors"
            title="Refresh pipelines"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          <button
            onClick={onOpenTriggerModal}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 transition-all hover:scale-[1.02]"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Trigger Demo Scenario</span>
          </button>
        </div>
      </div>

      {loading && (
        <div className="py-16 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <div className="w-7 h-7 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span>Loading registered pipelines from catalog...</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Pipelines Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {pipelines.map((pipe) => (
          <div
            key={pipe.id}
            className="p-5 rounded-2xl glass-panel glass-panel-hover flex flex-col justify-between space-y-4"
          >
            <div className="space-y-3">
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-navy-800 text-cyan-400 border border-navy-700 font-semibold tracking-wider block w-fit mb-1.5">
                    {pipe.code}
                  </span>
                  <h3 className="font-bold text-base text-white tracking-tight">{pipe.name}</h3>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shrink-0">
                  {pipe.status}
                </span>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                {pipe.description}
              </p>

              {/* Source -> Target badges */}
              <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800/80 space-y-2 text-xs font-mono">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500">Source:</span>
                  <span className="text-slate-300 font-semibold">{pipe.source_type}</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500">Target:</span>
                  <span className="text-cyan-400 font-semibold">{pipe.target_type}</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500">Schedule:</span>
                  <span className="text-slate-300">{pipe.schedule}</span>
                </div>
              </div>

              {/* Run Metrics Stats */}
              <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                <div className="p-2.5 rounded-lg bg-navy-950/50 border border-navy-800">
                  <span className="text-[11px] text-slate-500 block">Total Runs</span>
                  <span className="font-bold text-base text-white">{pipe.total_runs}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-navy-950/50 border border-navy-800">
                  <span className="text-[11px] text-slate-500 block">Success Rate</span>
                  <span className="font-bold text-base text-emerald-400">{pipe.success_rate}%</span>
                </div>
              </div>
            </div>

            {/* Footer with Actions */}
            <div className="border-t border-navy-800/80 pt-3 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-mono">
                {pipe.last_run_status ? (
                  <span className="flex items-center gap-1">
                    Last:{" "}
                    <strong
                      className={
                        pipe.last_run_status === "success" ? "text-emerald-400" : "text-rose-400"
                      }
                    >
                      {pipe.last_run_status}
                    </strong>
                  </span>
                ) : (
                  "No runs executed yet"
                )}
              </span>

              <Link
                to={`/pipelines/${pipe.id}`}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-navy-800 hover:bg-navy-700 text-cyan-400 hover:text-cyan-300 font-semibold text-xs border border-navy-700 transition-colors"
              >
                <span>Details & Logs</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
