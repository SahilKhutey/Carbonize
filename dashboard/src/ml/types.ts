export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  confidence: number;
  class_id: number;
  class_name: string;
}

export interface ModelPerformanceMetrics {
  timestamp: number;
  modelVersion: string;
  mAP50: number;
  mAP75: number;
  mAP50_95: number;
  precision: number;
  recall: number;
  f1Score: number;
  accuracy: number;
  inferenceLatencyMs: number;
  throughputFps: number;
  gpuUtilization: number;
  memoryUsageMb: number;
}

export interface PerClassMetrics {
  className: string;
  precision: number;
  recall: number;
  f1Score: number;
  support: number;
  tp: number;
  fp: number;
  fn: number;
  averagePrecision: number;
  confidenceHistogram: number[];
}

export interface ConfusionMatrix {
  classes: string[];
  matrix: number[][];
  normalized: number[][];
}

export interface DriftReport {
  timestamp: number;
  detection: 'drift_detected' | 'no_drift' | 'warning';
  overallScore: number;
  features: DriftFeature[];
  method: 'ks_test' | 'psi' | 'js_divergence' | 'classifier';
  referenceWindow: { start: number; end: number };
  testWindow: { start: number; end: number };
}

export interface DriftFeature {
  name: string;
  driftScore: number;
  pValue?: number;
  threshold: number;
  isDrifted: boolean;
  statistic: number;
  referenceDistribution: number[];
  testDistribution: number[];
}

export interface ConceptDriftReport {
  timestamp: number;
  detection: 'drift_detected' | 'no_drift';
  errorRate: number;
  baselineErrorRate: number;
  driftMagnitude: number;
  method: 'ddm' | 'eddm' | 'page_hinkley' | 'adwin';
}

export interface CalibrationData {
  bins: Array<{
    binCenter: number;
    averageConfidence: number;
    actualAccuracy: number;
    count: number;
    gap: number;
  }>;
  expectedCalibrationError: number;
  maximumCalibrationError: number;
  brierScore: number;
}

export interface FairnessMetrics {
  timestamp: number;
  protectedAttribute: string;
  groups: Array<{
    groupName: string;
    size: number;
    positiveRate: number;
    truePositiveRate: number;
    falsePositiveRate: number;
    precision: number;
  }>;
  metrics: {
    demographicParity: number;
    equalizedOdds: number;
    equalOpportunity: number;
    predictiveParity: number;
  };
}

export interface AblationResult {
  configName: string;
  metrics: {
    mAP50: number;
    mAP50_95: number;
    latencyMs: number;
  };
  features: Record<string, boolean>;
  trainingDurationMin: number;
  modelSizeMb: number;
}

export interface CurveData {
  points: Array<{ x: number; y: number; threshold?: number }>;
  auc: number;
  averagePrecision: number;
  optimalThreshold: number;
}
