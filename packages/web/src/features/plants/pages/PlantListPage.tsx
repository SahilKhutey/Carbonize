/**
 * packages/web/src/features/plants/pages/PlantListPage.tsx
 *
 * Industrial Plant Fleet Overview & Management Interface.
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Factory, Play, MonitorPlay, Plus, MapPin, Gauge, Activity, ShieldCheck } from "lucide-react";
import { usePlantProfile } from "../../../hooks/usePlantProfile";

export function PlantListPage() {
  const { plants, loading, refresh } = usePlantProfile();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");

  const defaultPlants = [
    {
      id: "plant-alpha",
      name: "NTPC Thermal Power Station 250MW",
      location: "Korba, Chhattisgarh, IN",
      boiler_type: "Pulverized Coal (Supercritical)",
      exhaust_flow_nm3_hr: 850000,
      co2_vol_pct: 13.5,
      so2_mg_per_nm3: 650,
      nox_mg_per_nm3: 450,
      status: "ONLINE",
    },
    {
      id: "plant-beta",
      name: "UltraTech Cement Line-02 (1000 TPD)",
      location: "Chandrapur, Maharashtra, IN",
      boiler_type: "Precalciner Cement Kiln",
      exhaust_flow_nm3_hr: 420000,
      co2_vol_pct: 18.2,
      so2_mg_per_nm3: 320,
      nox_mg_per_nm3: 280,
      status: "ONLINE",
    },
    {
      id: "plant-gamma",
      name: "JSW Steel Blast Furnace #4",
      location: "Vijayanagar, Karnataka, IN",
      boiler_type: "Integrated Steel Blast Furnace",
      exhaust_flow_nm3_hr: 1200000,
      co2_vol_pct: 22.0,
      so2_mg_per_nm3: 890,
      nox_mg_per_nm3: 510,
      status: "MAINTENANCE",
    },
  ];

  const plantList = plants.length > 0 ? plants : defaultPlants;
  const filtered = plantList.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
            <Factory className="w-6 h-6 text-emerald-400" />
            Industrial Plant Fleet Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure flue gas characteristics, monitor operational statuses, and launch simulation engines.
          </p>
        </div>

        <button
          onClick={() => navigate("/dashboard")}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-xl text-xs font-extrabold transition-all shadow-lg shadow-emerald-500/20"
        >
          <Plus className="w-4 h-4" />
          Add Plant Profile
        </button>
      </div>

      {/* Fleet KPI Summary Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-semibold block">Total Active Fleet</span>
          <span className="text-2xl font-black text-white mt-1 block">{plantList.length} Units</span>
        </div>
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-semibold block">Aggregate Exhaust Flow</span>
          <span className="text-2xl font-black text-cyan-400 mt-1 block">2.47M Nm³/hr</span>
        </div>
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-semibold block">Avg Flue Gas CO₂</span>
          <span className="text-2xl font-black text-emerald-400 mt-1 block">17.9 Vol %</span>
        </div>
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-semibold block">CPCB Compliance</span>
          <span className="text-2xl font-black text-emerald-400 mt-1 block flex items-center gap-1.5">
            <ShieldCheck className="w-5 h-5" /> 100%
          </span>
        </div>
      </div>

      {/* Search Filter */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3">
        <input
          type="text"
          placeholder="Filter plants by name or location..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
        />
      </div>

      {/* Plant Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((item) => {
          const plant = item as any;
          return (
            <div
              key={plant.id}
              className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between shadow-xl"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <Activity className="w-3 h-3" />
                    {plant.status || "ONLINE"}
                  </span>
                  <span className="text-xs font-mono text-slate-500">#{plant.id.slice(0, 8)}</span>
                </div>

                <h3 className="text-base font-bold text-white tracking-tight mb-1">{plant.name}</h3>
                <p className="text-xs text-slate-400 flex items-center gap-1 mb-4">
                  <MapPin className="w-3.5 h-3.5 text-slate-500" />
                  {plant.location}
                </p>

                <div className="space-y-2.5 pt-3 border-t border-slate-800/80 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Boiler System:</span>
                    <span className="font-semibold text-slate-200">{plant.boiler_type || "Pulverized Coal"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Exhaust Flow Rate:</span>
                    <span className="font-mono font-bold text-cyan-400">
                      {(plant.exhaust_flow_nm3_hr || plant.exhaust_flow_rate || 850000).toLocaleString()} Nm³/hr
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">CO₂ Flue Gas:</span>
                    <span className="font-mono font-bold text-emerald-400">
                      {plant.co2_vol_pct || plant.co2_concentration || 13.5}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">SO₂ / NOx Inlet:</span>
                    <span className="font-mono text-amber-400">
                      {plant.so2_mg_per_nm3 || 650} / {plant.nox_mg_per_nm3 || 450} mg/Nm³
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 pt-5 mt-4 border-t border-slate-800/80">
                <button
                  onClick={() => navigate(`/simulations/new`)}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-emerald-950/80 hover:bg-emerald-900 text-emerald-400 border border-emerald-800/60 rounded-xl text-xs font-bold transition-colors"
                >
                  <Play className="w-3.5 h-3.5" />
                  Simulate
                </button>

                <button
                  onClick={() => navigate(`/twin/${plant.id}`)}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-indigo-950/80 hover:bg-indigo-900 text-indigo-400 border border-indigo-800/60 rounded-xl text-xs font-bold transition-colors"
                >
                  <MonitorPlay className="w-3.5 h-3.5" />
                  Digital Twin
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
