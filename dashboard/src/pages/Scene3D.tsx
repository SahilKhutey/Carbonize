import { useState } from 'react';
import { Box, Maximize2, Camera } from 'lucide-react';
import { SceneViewer } from '@/components/scene/SceneViewer';
import { useSimulationStore } from '@/stores/simulationStore';
import { cn } from '@/lib/utils';

export function Scene3D() {
  const [showCO2, setShowCO2] = useState(true);
  const [showTrails, setShowTrails] = useState(true);
  const [showDetections, setShowDetections] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const selectedRobotId = useSimulationStore((s) => s.selectedRobotId);
  const robots = useSimulationStore((s) => Array.from(s.robots.values()));

  const selectedRobot = robots.find((r) => r.id === selectedRobotId);

  return (
    <div className={cn('flex h-full', fullscreen ? 'fixed inset-0 z-50 bg-slate-950' : '')}>
      <div className="flex-1 relative">
        <SceneViewer
          showCO2Field={showCO2}
          showPathTrails={showTrails}
          showDetectionMarkers={showDetections}
          showGrid={showGrid}
        />

        <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur rounded-lg p-3 space-y-2 border border-slate-800">
          <div className="text-xs font-semibold text-slate-300 mb-2">Layers</div>
          <ToggleRow label="CO₂ Field" value={showCO2} onChange={setShowCO2} />
          <ToggleRow label="Path Trails" value={showTrails} onChange={setShowTrails} />
          <ToggleRow label="Detections" value={showDetections} onChange={setShowDetections} />
          <ToggleRow label="Grid" value={showGrid} onChange={setShowGrid} />
          <hr className="border-slate-700" />
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="flex items-center gap-2 text-xs text-slate-300 hover:text-carbon-400 w-full"
          >
            <Maximize2 className="w-4 h-4" />
            {fullscreen ? 'Exit' : 'Fullscreen'}
          </button>
        </div>
      </div>

      {!fullscreen && (
        <div className="w-80 bg-slate-900 border-l border-slate-800 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Camera className="w-5 h-5 text-carbon-400" />
            Scene Inspector
          </h2>

          {selectedRobot ? (
            <div className="space-y-4">
              <div className="bg-slate-800 rounded-lg p-3">
                <h3 className="font-semibold text-slate-200 mb-2">{selectedRobot.name}</h3>
                <div className="space-y-1 text-sm">
                  <Row label="ID" value={selectedRobot.id} />
                  <Row label="Status" value={selectedRobot.status} />
                  <Row label="Battery" value={`${selectedRobot.battery.toFixed(0)}%`} />
                  <Row label="Position" value={`${selectedRobot.position.x.toFixed(2)}, ${selectedRobot.position.y.toFixed(2)}, ${selectedRobot.position.z.toFixed(2)}`} />
                  <Row label="Task" value={selectedRobot.currentTask ?? 'None'} />
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-3">
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Pose</h3>
                <div className="space-y-1 text-xs">
                  <Row label="Position" value={`[${selectedRobot.pose.position.map((n) => n.toFixed(2)).join(', ')}]`} />
                  <Row label="Orientation" value={`[${selectedRobot.pose.orientation.map((n) => n.toFixed(2)).join(', ')}]`} />
                </div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500 text-center py-8">
              <Box className="w-12 h-12 mx-auto mb-2 opacity-30" />
              Click a robot in the scene to inspect
            </div>
          )}

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-slate-300 mb-2">All Robots</h3>
            <div className="space-y-1">
              {robots.map((r) => (
                <button
                  key={r.id}
                  onClick={() => useSimulationStore.getState().setSelectedRobot(r.id)}
                  className={cn(
                    'w-full text-left px-3 py-2 rounded text-sm transition-colors',
                    selectedRobotId === r.id
                      ? 'bg-carbon-500/20 text-carbon-400'
                      : 'hover:bg-slate-800 text-slate-300'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span>{r.name}</span>
                    <span className="text-xs text-slate-500">{r.status}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ToggleRow({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-center justify-between text-xs cursor-pointer">
      <span className="text-slate-300">{label}</span>
      <button
        onClick={() => onChange(!value)}
        className={cn(
          'w-8 h-4 rounded-full transition-colors',
          value ? 'bg-carbon-500' : 'bg-slate-700'
        )}
      >
        <div className={cn(
          'w-3 h-3 rounded-full bg-white transition-transform',
          value ? 'translate-x-4' : 'translate-x-0.5'
        )} />
      </button>
    </label>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}:</span>
      <span className="text-slate-200 font-mono text-xs">{value}</span>
    </div>
  );
}
