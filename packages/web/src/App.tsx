import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { usePlantProfile } from './hooks/usePlantProfile.ts';
import { PlantForm } from './components/PlantForm.tsx';
import { SimulationDashboard } from './components/SimulationDashboard.tsx';

// Feature imports
import { TwinPage }               from './features/digital-twin/index.tsx';
import { OperatorDashboardPage }  from './features/operator/index.tsx';
import { ExecutiveDashboard }     from './features/executive/index.tsx';
import { AlarmHistory }           from './features/operator/pages/AlarmHistory.tsx';
import { ShiftHandover }          from './features/operator/pages/ShiftHandover.tsx';
import { ResultsPage }            from './features/simulation-results/pages/ResultsPage.tsx';
import { ExperimentalLab }        from './features/experimental/pages/ExperimentalLab.tsx';

// Phase 5C Components
import { SimulationList }         from './features/simulation/pages/SimulationList.tsx';
import { SimulationWizard }       from './features/simulation/pages/SimulationWizard.tsx';
import { SimulationDetail }       from './features/simulation/pages/SimulationDetail.tsx';

// ---------------------------------------------------------------------------
// Main legacy dashboard (plant selection → simulation)
// ---------------------------------------------------------------------------

const MainDashboard: React.FC = () => {
  const { plants, loading, refresh } = usePlantProfile();
  const [selectedPlantId, setSelectedPlantId] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans">

      <header className="border-b border-slate-800 bg-slate-900 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-emerald-400 font-extrabold text-2xl tracking-tight">
            🌿 CarbonLattice Tech
          </span>
          <div className="h-6 w-px bg-slate-800 hidden md:block" />
          <p className="text-xs text-slate-400 hidden md:block">
            CBMS Digital Control System
          </p>
        </div>

        {/* Jump to dashboards */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/operator/live')}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-800/60 border border-amber-700 text-amber-300 hover:bg-amber-700 transition-colors"
          >
            🔧 Operator DCS
          </button>
          <button
            onClick={() => navigate('/executive/dashboard')}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-900/60 border border-blue-700 text-blue-300 hover:bg-blue-800 transition-colors"
          >
            📊 Executive View
          </button>
        </div>
      </header>

      <div className="flex-1 max-w-7xl mx-auto w-full p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">CMBSG Digital Twin Dashboard</h1>
            <p className="text-xs text-slate-400 mt-0.5">Configure plant parameters and simulate carbon crystallization.</p>
          </div>
          <button
            onClick={() => setShowCreateForm(p => !p)}
            className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold px-4 py-2 rounded-lg transition-all"
          >
            {showCreateForm ? 'View Simulations' : 'Create New Plant Profile'}
          </button>
        </div>

        {showCreateForm ? (
          <PlantForm onSuccess={() => { setShowCreateForm(false); refresh(); }} />
        ) : (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-3 items-center">
              <span className="text-xs font-semibold text-slate-400">Select Plant Profile:</span>
              {loading ? (
                <span className="text-xs text-slate-500">Loading plants…</span>
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

            {selectedPlantId && (
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => navigate(`/twin/${selectedPlantId}`)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-700/80 hover:bg-emerald-600 text-white rounded-lg text-xs font-semibold border border-emerald-600 transition-colors"
                >
                  🔴 Live Digital Twin
                </button>
                <button
                  onClick={() => navigate(`/operator/live`)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-amber-800/60 hover:bg-amber-700 text-amber-200 rounded-lg text-xs font-semibold border border-amber-700 transition-colors"
                >
                  🔧 Operator DCS
                </button>
              </div>
            )}

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

import { AppShell }               from './components/layout/AppShell.tsx';
import { LoginPage }              from './components/auth/LoginPage.tsx';
import { ProtectedRoute }         from './components/auth/ProtectedRoute.tsx';

// ---------------------------------------------------------------------------
// App shell — full route tree with role-based views
// ---------------------------------------------------------------------------

export const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      {/* ── Public Routes ── */}
      <Route path="/login" element={<LoginPage />} />
      <Route 
        path="/unauthorized" 
        element={
          <div className="bg-slate-950 text-white min-h-screen flex flex-col items-center justify-center text-center p-8">
            <h1 className="text-3xl font-bold mb-4 text-red-400">403 - Unauthorized</h1>
            <p className="text-slate-400">You do not have permission to view this page.</p>
          </div>
        } 
      />

      {/* ── Operator DCS routes (Standalone, No Sidebar) ── */}
      <Route path="/operator/*" element={
        <ProtectedRoute allowedRoles={['operator', 'admin']}>
          <Routes>
            <Route path="live" element={<OperatorDashboardPage />} />
            <Route path="live/:plantId" element={<OperatorDashboardPage />} />
            <Route path="schematic/:plantId" element={<div className="bg-slate-950 text-slate-100 min-h-screen flex items-center justify-center">Plant Schematic — full page</div>} />
            <Route path="alarms" element={<AlarmHistory />} />
            <Route path="handover" element={<ShiftHandover />} />
            <Route path="*" element={<Navigate to="live" replace />} />
          </Routes>
        </ProtectedRoute>
      } />

      {/* ── Digital Twin real-time view (Standalone, No Sidebar) ── */}
      <Route path="/twin/:plantId" element={
        <ProtectedRoute allowedRoles={['engineer', 'admin', 'manager']}>
          <div className="bg-slate-950 text-slate-100 min-h-screen">
            <TwinPage />
          </div>
        </ProtectedRoute>
      } />

      {/* ── App Shell (Protected, Shared Sidebar Layout) ── */}
      <Route path="/" element={
        <ProtectedRoute>
          <AppShell />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* General Dashboard */}
        <Route path="dashboard" element={<MainDashboard />} />

        {/* 5C Placeholders */}
        <Route path="plants" element={<div className="p-4 text-slate-400">Plant List (Task 5C)</div>} />
        <Route path="plants/:id" element={<div className="p-4 text-slate-400">Plant Detail (Task 5C)</div>} />
        
        <Route path="simulations" element={<SimulationList />} />
        <Route path="simulations/new" element={<SimulationWizard />} />
        <Route path="simulations/:id" element={<SimulationDetail />} />
        
        {/* Simulation Results (UQ) */}
        <Route path="simulations/:id/results" element={<ResultsPage />} />
        <Route path="simulations/demo"        element={<ResultsPage />} />
        <Route path="experimental"            element={<ExperimentalLab />} />

        {/* Executive / Report routes */}
        <Route path="executive/*" element={
          <ProtectedRoute allowedRoles={['manager', 'admin']}>
            <Routes>
              <Route path="dashboard" element={<ExecutiveDashboard />} />
              <Route path="plants" element={<div className="flex h-full items-center justify-center text-slate-600">Plant Table</div>} />
              <Route path="plants/:plantId" element={<div className="flex h-full items-center justify-center text-slate-600">Plant Detail</div>} />
              <Route path="reports" element={<div className="flex h-full items-center justify-center text-slate-600">Report Builder</div>} />
              <Route path="analytics" element={<div className="flex h-full items-center justify-center text-slate-600">Analytics</div>} />
              <Route path="*" element={<Navigate to="dashboard" replace />} />
            </Routes>
          </ProtectedRoute>
        } />
        
        {/* Reports & Compliance (from sidebar) */}
        <Route path="reports" element={<Navigate to="/executive/reports" replace />} />
        <Route path="compliance" element={<div className="p-4 text-slate-400">Compliance Dashboard</div>} />
      </Route>

      {/* ── Fallback ── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);
