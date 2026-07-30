import { useState } from 'react';
import { Trajectory3DChart } from './3DTrajectoryChart';
import type { TrajectoryPoint } from './3DTrajectoryChart';

export function TrajectoryChartWrapper({ data }: { data: any[] }) {
  const [selectedPoint, setSelectedPoint] = useState<{ trajectoryId: string; point: TrajectoryPoint } | null>(null);
  
  return (
    <div className="grid grid-cols-12 gap-3">
      <div className="col-span-9">
        <Trajectory3DChart
          trajectories={data}
          onPointClick={(id, point) => setSelectedPoint({ trajectoryId: id, point })}
        />
      </div>
      <div className="col-span-3 bg-surface border border-border rounded-theme-md p-3">
        <h3 className="font-semibold text-text mb-2">Point Inspector</h3>
        {selectedPoint ? (
          <div className="space-y-2 text-sm">
            <div><span className="text-text-tertiary">Trajectory:</span> <span className="text-text font-mono ml-1">{selectedPoint.trajectoryId}</span></div>
            <div><span className="text-text-tertiary">Timestamp:</span> <span className="text-text font-mono ml-1">{new Date(selectedPoint.point.timestamp).toLocaleTimeString()}</span></div>
            <div><span className="text-text-tertiary">Coordinates:</span> <span className="text-text font-mono ml-1">{selectedPoint.point.position.map((n: number) => n.toFixed(2)).join(', ')}</span></div>
            {selectedPoint.point.velocity !== undefined && (
              <div><span className="text-text-tertiary">Velocity:</span> <span className="text-text font-mono ml-1">{selectedPoint.point.velocity.toFixed(2)} m/s</span></div>
            )}
            {selectedPoint.point.event && (
              <div><span className="text-text-tertiary">Event:</span> <span className="text-primary-400 font-mono ml-1">{selectedPoint.point.event}</span></div>
            )}
          </div>
        ) : (
          <p className="text-text-tertiary text-sm">Click any point on the 3D trajectory to inspect telemetry</p>
        )}
      </div>
    </div>
  );
}
