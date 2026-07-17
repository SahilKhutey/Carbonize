import React, { useState } from 'react';
import { usePlantProfile } from './hooks/usePlantProfile.ts';
import { PlantForm } from './components/PlantForm.tsx';
import { SimulationDashboard } from './components/SimulationDashboard.tsx';

export const App: React.FC = () => {
  const { plants, loading, refresh } = usePlantProfile();
  const [selectedPlantId, setSelectedPlantId] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans">
      
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-emerald-400 font-extrabold text-2xl tracking-tight flex items-center gap-2">
            <span className="material-icons">waves</span> CarbonLattice Tech
          </span>
          <div className="h-6 w-px bg-slate-800 hidden md:block" />
          <p className="text-xs text-slate-400 hidden md:block">
            Continuous Biomineralization & Multi-Pollutant Solidification Grid — DCS V1.2
          </p>
        </div>
      </header>

      {/* Main content grid */}
      <div className="flex-1 max-w-7xl mx-auto w-full p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">CMBSG Digital Twin Dashboard</h1>
            <p className="text-xs text-slate-400 mt-0.5">Configure plant parameters and simulate real-time carbon crystallization.</p>
          </div>
          <button
            onClick={() => setShowCreateForm(p => !p)}
            className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold px-4 py-2 rounded-lg transition-all"
          >
            {showCreateForm ? 'View Simulation list' : 'Create New Plant Profile'}
          </button>
        </div>

        {showCreateForm ? (
          <PlantForm
            onSuccess={() => {
              setShowCreateForm(false);
              refresh();
            }}
          />
        ) : (
          <div className="space-y-6">
            {/* Plant selection row */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-3 items-center">
              <span className="text-xs font-semibold text-slate-400">Select Plant Profile:</span>
              {loading ? (
                <span className="text-xs text-slate-500">Loading plants...</span>
              ) : plants.length > 0 ? (
                <div className="flex gap-2 flex-wrap">
                  {plants.map(p => (
                    <button
                      key={p.id}
                      onClick={() => setSelectedPlantId(p.id)}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                        selectedPlantId === p.id
                          ? 'bg-emerald-500 border-emerald-500 text-slate-950 font-bold'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      {p.name} ({p.location})
                    </button>
                  ))}
                </div>
              ) : (
                <span className="text-xs text-slate-500">No plant profiles found. Create one to begin.</span>
              )}
            </div>

            {selectedPlantId ? (
              <SimulationDashboard plantId={selectedPlantId} />
            ) : (
              <div className="bg-slate-900/20 border border-slate-800 rounded-2xl p-16 text-center text-slate-500 flex flex-col items-center justify-center gap-2">
                <span className="text-emerald-400 font-bold text-sm">Select a Plant Profile to Start</span>
                <p className="max-w-xs text-xs">Simulations require exhaust characteristics defined by a plant profile.</p>
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
};
