import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { Robot, Detection, SimulationState, Alert } from '@/types';

interface SimulationStore {
  simState: SimulationState | null;
  robots: Map<string, Robot>;
  detections: Detection[];
  alerts: Alert[];
  selectedRobotId: string | null;
  recentTelemetry: Array<{ ts: number; value: number }>;

  setSimState: (state: SimulationState) => void;
  updateRobot: (robot: Robot) => void;
  addDetection: (det: Detection) => void;
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (id: string) => void;
  setSelectedRobot: (id: string | null) => void;
  pushTelemetry: (value: number) => void;
  clearDetections: () => void;
}

export const useSimulationStore = create<SimulationStore>()(
  subscribeWithSelector((set) => ({
    simState: null,
    robots: new Map(),
    detections: [],
    alerts: [],
    selectedRobotId: null,
    recentTelemetry: [],

    setSimState: (state) => set({ simState: state }),
    updateRobot: (robot) =>
      set((s) => {
        const next = new Map(s.robots);
        next.set(robot.id, robot);
        return { robots: next };
      }),
    addDetection: (det) =>
      set((s) => ({ detections: [det, ...s.detections].slice(0, 500) })),
    addAlert: (alert) =>
      set((s) => ({
        alerts: [alert, ...s.alerts].slice(0, 200),
      })),
    acknowledgeAlert: (id) =>
      set((s) => ({
        alerts: s.alerts.map((a) =>
          a.id === id ? { ...a, acknowledged: true, acknowledgedAt: Date.now() } : a
        ),
      })),
    setSelectedRobot: (id) => set({ selectedRobotId: id }),
    pushTelemetry: (value) =>
      set((s) => ({
        recentTelemetry: [
          ...s.recentTelemetry.slice(-119),
          { ts: Date.now(), value },
        ],
      })),
    clearDetections: () => set({ detections: [] }),
  }))
);

export const selectActiveRobots = (s: SimulationStore) =>
  Array.from(s.robots.values()).filter((r) => r.status !== 'offline');

export const selectUnacknowledgedAlerts = (s: SimulationStore) =>
  s.alerts.filter((a) => !a.acknowledged);

export const selectCriticalAlerts = (s: SimulationStore) =>
  s.alerts.filter((a) => !a.acknowledged && (a.severity === 'critical' || a.severity === 'error'));
