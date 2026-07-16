/**
 * packages/web/src/features/simulation/pages/SimulationList.tsx
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Play, CheckCircle2, XCircle, Clock, Plus, Search, Filter } from "lucide-react";

export type SimStatus = "PENDING" | "RUNNING" | "COMPLETE" | "FAILED";

export interface SimulationRun {
  id: string;
  name: string;
  plantId: string;
  status: SimStatus;
  createdAt: string;
  duration?: string;
  progress?: number; // 0-100
}

// Mock data for initial rendering
const MOCK_RUNS: SimulationRun[] = [
  { id: "sim-001", name: "High-Temp Stress Test", plantId: "plant-alpha", status: "COMPLETE", createdAt: "2026-07-15T08:30:00Z", duration: "14m 20s" },
  { id: "sim-002", name: "Winter Flow Rate Opt", plantId: "plant-beta", status: "FAILED", createdAt: "2026-07-15T09:15:00Z", duration: "2m 10s" },
  { id: "sim-003", name: "Carbon Cost Sensitivity", plantId: "plant-alpha", status: "RUNNING", createdAt: "2026-07-16T11:40:00Z", progress: 45 },
  { id: "sim-004", name: "Enzyme Concentration Map", plantId: "plant-gamma", status: "PENDING", createdAt: "2026-07-16T11:45:00Z" },
];

export function SimulationList() {
  const [runs, setRuns] = useState<SimulationRun[]>(MOCK_RUNS);
  const [filter, setFilter] = useState<SimStatus | "ALL">("ALL");
  const navigate = useNavigate();

  // Mock live updates for RUNNING simulations
  useEffect(() => {
    const interval = setInterval(() => {
      setRuns((currentRuns) =>
        currentRuns.map((run) => {
          if (run.status === "RUNNING" && run.progress !== undefined) {
            const newProgress = Math.min(run.progress + Math.floor(Math.random() * 10), 100);
            return {
              ...run,
              progress: newProgress,
              status: newProgress === 100 ? "COMPLETE" : "RUNNING",
              duration: newProgress === 100 ? "15m 00s" : undefined,
            };
          }
          return run;
        })
      );
    }, 2000); // Faster for demo purposes

    return () => clearInterval(interval);
  }, []);

  const filteredRuns = filter === "ALL" ? runs : runs.filter((r) => r.status === filter);

  const StatusBadge = ({ status, progress }: { status: SimStatus; progress?: number }) => {
    switch (status) {
      case "COMPLETE":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3.5 h-3.5" /> Complete</span>;
      case "FAILED":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20"><XCircle className="w-3.5 h-3.5" /> Failed</span>;
      case "RUNNING":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Running {progress !== undefined ? `(${progress}%)` : ''}
          </span>
        );
      case "PENDING":
      default:
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20"><Clock className="w-3.5 h-3.5" /> Pending</span>;
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Simulations</h1>
          <p className="text-sm text-slate-400 mt-1">Manage and monitor carbon crystallization models.</p>
        </div>
        <button
          onClick={() => navigate("/simulations/new")}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-emerald-500 focus:outline-none"
        >
          <Plus className="w-4 h-4" />
          New Simulation
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row gap-4 justify-between">
          <div className="relative max-w-md w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search simulations..."
              className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2 pl-9 pr-4 text-sm text-white placeholder-slate-500 focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition-shadow"
            />
          </div>
          
          <div className="flex items-center gap-2 shrink-0">
            <Filter className="w-4 h-4 text-slate-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as SimStatus | "ALL")}
              className="bg-slate-950 border border-slate-700 rounded-lg py-1.5 pl-3 pr-8 text-sm text-white focus:ring-1 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="RUNNING">Running</option>
              <option value="PENDING">Pending</option>
              <option value="COMPLETE">Complete</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-400">
            <thead className="bg-slate-950/50 text-xs uppercase text-slate-500 font-semibold border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Name / ID</th>
                <th className="px-6 py-4">Plant</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Started</th>
                <th className="px-6 py-4">Duration</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredRuns.map((run) => (
                <tr 
                  key={run.id} 
                  className="hover:bg-slate-800/30 transition-colors group cursor-pointer"
                  onClick={() => navigate(`/simulations/${run.id}`)}
                >
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-200 group-hover:text-emerald-400 transition-colors">{run.name}</div>
                    <div className="text-xs text-slate-500 font-mono mt-0.5">{run.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs bg-slate-800 text-slate-300">
                      {run.plantId}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={run.status} progress={run.progress} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {new Date(run.createdAt).toLocaleString(undefined, { 
                      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                    })}
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {run.duration || '—'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded-md transition-colors"
                      aria-label="View Details"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/simulations/${run.id}`);
                      }}
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              
              {filteredRuns.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <p className="text-slate-500 mb-2">No simulations found matching this filter.</p>
                    <button 
                      onClick={() => setFilter("ALL")}
                      className="text-sm text-emerald-400 hover:underline"
                    >
                      Clear filters
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
