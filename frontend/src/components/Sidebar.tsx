import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  GitBranch,
  AlertTriangle,
  ShieldCheck,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Database,
  Activity,
} from "lucide-react";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const navItems = [
    { name: "Overview", path: "/", icon: LayoutDashboard },
    { name: "Pipelines", path: "/pipelines", icon: GitBranch },
    { name: "Incidents", path: "/incidents", icon: AlertTriangle },
    { name: "Data Quality", path: "/quality", icon: ShieldCheck },
    { name: "Recovery Center", path: "/recovery", icon: RefreshCw },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-screen z-30 transition-all duration-300 flex flex-col border-r border-navy-700/60 bg-navy-900/95 backdrop-blur-md ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-navy-700/60">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 via-blue-600 to-violet-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 shrink-0">
            <Activity className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                DataPulse
              </span>
              <span className="text-[10px] text-cyan-400/80 font-mono tracking-wider uppercase">
                Detect • Diagnose • Recover
              </span>
            </div>
          )}
        </div>
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md hover:bg-navy-800 text-slate-400 hover:text-slate-200 transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-4 px-3 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500/15 to-blue-600/15 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10"
                    : "text-slate-400 hover:text-slate-200 hover:bg-navy-800/60 border border-transparent"
                }`
              }
              title={collapsed ? item.name : undefined}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Engine Status Footer */}
      <div className="p-3 border-t border-navy-700/60">
        <div
          className={`flex items-center gap-2.5 px-3 py-2 rounded-lg bg-navy-950/60 border border-navy-700/40 ${
            collapsed ? "justify-center" : ""
          }`}
        >
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
          {!collapsed && (
            <div className="flex flex-col text-xs">
              <span className="text-slate-300 font-medium flex items-center gap-1">
                <Database className="w-3 h-3 text-cyan-400" /> Live DB Connected
              </span>
              <span className="text-[10px] text-slate-500 font-mono">PostgreSQL / SQLite</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
