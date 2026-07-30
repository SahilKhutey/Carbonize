import type { BoundingBox } from '@/ml/types';

export interface TestConfig {
  modelId: string;
  confidenceThreshold: number;
  iouThreshold: number;
  maxDetections: number;
  edgeSimulator?: EdgeSimulatorConfig;
  classes?: string[];
  returnAnnotatedImage: boolean;
}

export interface EdgeSimulatorConfig {
  enabled: boolean;
  device: 'jetson_nano' | 'jetson_xavier' | 'cpu_only' | 'raspberry_pi';
  simulateLatencyMs?: number;
  memoryLimitMb?: number;
  powerLimitWatts?: number;
}

export interface TestSample {
  id: string;
  imageUrl: string;
  imageData?: string;
  groundTruth?: BoundingBox[];
  predictions?: BoundingBox[];
  inferenceTimeMs?: number;
  correct?: boolean;
  iou?: number;
}

export interface TestRunResults {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  totalSamples: number;
  processedSamples: number;
  failedSamples: number;
  metrics: {
    mAP50: number;
    mAP50_95: number;
    precision: number;
    recall: number;
    f1: number;
    avgInferenceMs: number;
  };
  perClassMetrics?: Record<string, {
    precision: number;
    recall: number;
    f1Score: number;
    support: number;
  }>;
  confusionMatrix?: {
    classes: string[];
    matrix: number[][];
  };
  startedAt?: string;
  completedAt?: string;
  durationSeconds?: number;
}

export interface ABTestComparison {
  modelA: string;
  modelB: string;
  results: {
    sampleId: string;
    imageUrl: string;
    predictionsA: BoundingBox[];
    predictionsB: BoundingBox[];
    groundTruth?: BoundingBox[];
    winnerA?: boolean;
    winnerB?: boolean;
    iouA: number;
    iouB: number;
    timeA: number;
    timeB: number;
  }[];
  summary: {
    winsA: number;
    winsB: number;
    ties: number;
    avgTimeA: number;
    avgTimeB: number;
    avgIoUA: number;
    avgIoUB: number;
  };
}
