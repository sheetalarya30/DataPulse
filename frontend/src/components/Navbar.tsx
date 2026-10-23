import React, { useState, useEffect } from "react";
import { Play, Activity, Server, AlertCircle, RefreshCw } from "lucide-react";
import { api } from "../api/client";

interface NavbarProps {
  onOpenTriggerModal: () => void;
  title?: string;
  subtitle?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenTriggerModal,
  title = "Overview",
  subtitle = "Data Pipeline Health & Diagnostics Dashboard",
}) => {
  const [healthStatus, setHealthStatus] = useState<string>("checking");
  const [dbDialect, setDbDialect] = useState<string>("");

  useEffect(() => {
    api
      .getHealth()
      .then((res) => {
        setHealthStatus(res.status);
        setDbDialect(res.database.dialect);
      })
      .catch(() => setHealthStatus("degraded"));
  }, []);

  return (
    <header className="h-16 border-b border-navy-700/60 bg-navy-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-lg font-bold text-slate-100 tracking-tight flex items-center gap-2">
          {title}
        </h1>
        <p className="text-xs text-slate-400 font-normal">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* System Health Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-navy-800/80 border border-navy-700 text-xs">
          <div
            className={`w-2 h-2 rounded-full ${
              healthStatus === "healthy"
                ? "bg-emerald-400 animate-pulse"
                : healthStatus === "checking"
                ? "bg-amber-400"
                : "bg-rose-400"
            }`}
          />
          <span className="text-slate-300 font-mono text-[11px]">
            API: <strong className="text-emerald-400 capitalize">{healthStatus}</strong>
            {dbDialect && <span className="text-slate-500 ml-1">({dbDialect})</span>}
          </span>
        </div>

        {/* Trigger Demo Run Button */}
        <button
          onClick={onOpenTriggerModal}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-semibold text-xs tracking-wide shadow-md shadow-cyan-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Execute Demo Scenario</span>
        </button>
      </div>
    </header>
  );
};
