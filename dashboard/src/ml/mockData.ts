import type {
  ModelPerformanceMetrics, DriftReport, ConfusionMatrix, 
  CalibrationData, FairnessMetrics, AblationResult, CurveData,
  PerClassMetrics, ConceptDriftReport,
} from './types';

const CLASSES = ['co2_emitter', 'capture_unit', 'industrial_equipment', 'pipeline', 'valve', 'tank'];

export function generatePerformanceHistory(hours = 24): ModelPerformanceMetrics[] {
  const data: ModelPerformanceMetrics[] = [];
  const now = Date.now();
  
  for (let i = hours * 60; i >= 0; i -= 15) {
    const t = now - i * 60_000;
    const trend = Math.sin(i / 200) * 0.05;
    const noise = (Math.random() - 0.5) * 0.02;
    
    data.push({
      timestamp: t,
      modelVersion: '1.5.0',
      mAP50: 0.88 + trend + noise,
      mAP75: 0.78 + trend + noise,
      mAP50_95: 0.65 + trend * 0.8 + noise,
      precision: 0.85 + trend + noise,
      recall: 0.82 + trend + noise * 0.5,
      f1Score: 0.835 + trend + noise,
      accuracy: 0.91 + trend + noise,
      inferenceLatencyMs: 18 + Math.random() * 4,
      throughputFps: 52 + Math.random() * 5,
      gpuUtilization: 65 + Math.random() * 20,
      memoryUsageMb: 1024 + Math.random() * 100,
    });
  }
  return data;
}

export function generatePerClassMetrics(): PerClassMetrics[] {
  return CLASSES.map((cls) => {
    const support = Math.floor(500 + Math.random() * 1500);
    const precision = 0.75 + Math.random() * 0.2;
    const recall = 0.70 + Math.random() * 0.25;
    const tp = Math.floor(support * recall);
    const fn = support - tp;
    const fp = Math.floor(tp * (1 - precision) / precision);
    
    return {
      className: cls,
      precision,
      recall,
      f1Score: 2 * (precision * recall) / (precision + recall),
      support,
      tp, fp, fn,
      averagePrecision: 0.75 + Math.random() * 0.2,
      confidenceHistogram: Array.from({ length: 10 }, () => Math.floor(Math.random() * 100)),
    };
  });
}

export function generateConfusionMatrix(): ConfusionMatrix {
  const n = CLASSES.length;
  const matrix = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => {
      if (i === j) return Math.floor(800 + Math.random() * 200);
      return Math.floor(Math.random() * 30);
    })
  );
  
  const normalized = matrix.map((row) => {
    const sum = row.reduce((a, b) => a + b, 0);
    return row.map((v) => v / sum);
  });
  
  return { classes: CLASSES, matrix, normalized };
}

export function generateCalibrationData(): CalibrationData {
  const bins = Array.from({ length: 10 }, (_, i) => {
    const binCenter = (i + 0.5) / 10;
    const actualAccuracy = binCenter + (Math.random() - 0.5) * 0.1;
    return {
      binCenter,
      averageConfidence: binCenter,
      actualAccuracy,
      count: Math.floor(100 + Math.random() * 200),
      gap: actualAccuracy - binCenter,
    };
  });
  
  const ece = bins.reduce((acc, b) => acc + Math.abs(b.gap) * b.count / bins.reduce((s, x) => s + x.count, 0), 0);
  const mce = Math.max(...bins.map((b) => Math.abs(b.gap)));
  
  return {
    bins,
    expectedCalibrationError: ece,
    maximumCalibrationError: mce,
    brierScore: 0.08 + Math.random() * 0.04,
  };
}

export function generateDriftReport(): DriftReport {
  const features = ['brightness', 'contrast', 'saturation', 'edge_density', 'noise_level', 'size_avg', 'aspect_ratio']
    .map((name) => {
      const driftScore = Math.random();
      const isDrifted = driftScore > 0.7;
      return {
        name,
        driftScore,
        pValue: isDrifted ? Math.random() * 0.05 : Math.random() * 0.5,
        threshold: 0.7,
        isDrifted,
        statistic: Math.random() * 0.5,
        referenceDistribution: Array.from({ length: 20 }, () => Math.random()),
        testDistribution: Array.from({ length: 20 }, () => Math.random() * (isDrifted ? 1.3 : 1.0)),
      };
    });
  
  const driftCount = features.filter((f) => f.isDrifted).length;
  
  return {
    timestamp: Date.now(),
    detection: driftCount > 0 ? (driftCount > 2 ? 'drift_detected' : 'warning') : 'no_drift',
    overallScore: driftCount / features.length,
    features,
    method: 'ks_test',
    referenceWindow: { start: Date.now() - 7 * 86_400_000, end: Date.now() - 86_400_000 },
    testWindow: { start: Date.now() - 86_400_000, end: Date.now() },
  };
}

export function generateConceptDriftReport(): ConceptDriftReport {
  return {
    timestamp: Date.now(),
    detection: Math.random() > 0.7 ? 'drift_detected' : 'no_drift',
    errorRate: 0.05 + Math.random() * 0.15,
    baselineErrorRate: 0.05,
    driftMagnitude: Math.random() * 0.5,
    method: 'eddm',
  };
}

export function generateFairnessMetrics(): FairnessMetrics {
  const groups = ['lighting_low', 'lighting_high', 'weather_clear', 'weather_foggy', 'distance_close', 'distance_far']
    .map((name) => ({
      groupName: name,
      size: Math.floor(500 + Math.random() * 1500),
      positiveRate: 0.4 + Math.random() * 0.4,
      truePositiveRate: 0.7 + Math.random() * 0.25,
      falsePositiveRate: Math.random() * 0.1,
      precision: 0.7 + Math.random() * 0.25,
    }));
  
  return {
    timestamp: Date.now(),
    protectedAttribute: 'lighting_condition',
    groups,
    metrics: {
      demographicParity: Math.abs(groups[0].positiveRate - groups[1].positiveRate),
      equalizedOdds: 0.08 + Math.random() * 0.05,
      equalOpportunity: Math.abs(groups[0].truePositiveRate - groups[1].truePositiveRate),
      predictiveParity: Math.abs(groups[0].precision - groups[1].precision),
    },
  };
}

export function generateAblationResults(): AblationResult[] {
  const baseFeatures = { backbone: true, fpn: true, data_aug: true, multi_scale: true, attention: true };
  const configs = ['Baseline', 'No FPN', 'No Aug', 'No Multi-Scale', 'No Attention', 'Full'];
  
  return configs.map((name) => {
    const features = { ...baseFeatures };
    if (name === 'No FPN') features.fpn = false;
    if (name === 'No Aug') features.data_aug = false;
    if (name === 'No Multi-Scale') features.multi_scale = false;
    if (name === 'No Attention') features.attention = false;
    
    const mapDegradation = 1 - (Object.values(features).filter(Boolean).length / Object.keys(baseFeatures).length) * 0.1;
    
    return {
      configName: name,
      metrics: {
        mAP50: (0.88 * mapDegradation) + Math.random() * 0.02,
        mAP50_95: (0.65 * mapDegradation) + Math.random() * 0.02,
        latencyMs: 18 + Math.random() * 5,
      },
      features,
      trainingDurationMin: 60 + Math.random() * 90,
      modelSizeMb: 14 + Math.random() * 2,
    };
  });
}

export function generateROCCurve(): CurveData {
  const points = Array.from({ length: 100 }, (_, i) => {
    const fpr = i / 99;
    const tpr = 1 - Math.pow(1 - fpr, 3) + Math.random() * 0.02;
    return { x: fpr, y: Math.min(1, tpr), threshold: 1 - i / 99 };
  });
  const auc = 0.93 + Math.random() * 0.04;
  return { points, auc, averagePrecision: 0.91, optimalThreshold: 0.65 };
}
