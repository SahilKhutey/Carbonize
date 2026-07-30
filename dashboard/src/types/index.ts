export interface Robot {
  id: string;
  name: string;
  status: 'idle' | 'navigating' | 'capturing' | 'charging' | 'error' | 'offline';
  position: { x: number; y: number; z: number };
  battery: number;
  pose: {
    position: [number, number, number];
    orientation: [number, number, number, number];
  };
  currentTask?: string;
  lastSeen: string;
}

export interface CO2Reading {
  timestamp: number;
  robotId: string;
  ppm: number;
  temperature: number;
  humidity: number;
  position: { x: number; y: number; z: number };
}

export interface Detection {
  id: string;
  timestamp: number;
  robotId: string;
  class: string;
  confidence: number;
  bbox: [number, number, number, number];
  imageUrl: string;
  modelVersion: string;
  position?: { x: number; y: number; z: number };
}

export type ModelStage = 'None' | 'Staging' | 'Production' | 'Archived';

export interface MLModel {
  id: string;
  name: string;
  version: string;
  stage: ModelStage;
  format: 'onnx' | 'engine' | 'openvino' | 'tflite';
  size: number;
  metrics: {
    mAP50: number;
    mAP50_95: number;
    precision: number;
    recall: number;
    latencyMs: number;
  };
  trafficPercent: number;
  registeredAt: string;
  description?: string;
}

export interface SimulationState {
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  currentTime: number;
  realTime: number;
  speedFactor: number;
  robots: Robot[];
  environment: {
    co2Level: number;
    co2Concentration: number;
    temperature: number;
    humidity: number;
    lightIntensity: number;
    windSpeed: number;
  };
  fog: { enabled: boolean; density: number };
  scenarios: SimulationScenario[];
}

export interface SimulationScenario {
  id: string;
  name: string;
  description: string;
  duration: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  metrics?: {
    detectionsCount: number;
    co2Captured: number;
    avgConfidence: number;
  };
}

export interface Alert {
  id: string;
  type: 'co2_high' | 'robot_error' | 'battery_low' | 'model_failure' | 'latency_high' | 'offline';
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: number;
  robotId?: string;
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: number;
}

export interface Experiment {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'running' | 'paused' | 'completed' | 'abandoned';
  variants: ExperimentVariant[];
  startTime?: string;
  endTime?: string;
  results?: {
    isSignificant: boolean;
    pValue: number;
    effectSize: number;
    confidenceInterval: [number, number];
    winner?: string;
  };
}

export interface ExperimentVariant {
  name: string;
  modelId: string;
  trafficWeight: number;
  isControl: boolean;
  samples: number;
  metrics: {
    avgLatencyMs: number;
    avgConfidence: number;
    successRate: number;
  };
}

export type WSMessage =
  | { type: 'telemetry'; data: CO2Reading }
  | { type: 'detection'; data: Detection }
  | { type: 'robot_state'; data: Robot }
  | { type: 'sim_state'; data: SimulationState }
  | { type: 'alert'; data: Alert }
  | { type: 'model_update'; data: MLModel }
  | { type: 'experiment_update'; data: Experiment };
