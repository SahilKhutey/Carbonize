import { api } from '@/lib/api';
import type {
  ModelPerformanceMetrics, DriftReport, ConceptDriftReport,
  ConfusionMatrix, CalibrationData, FairnessMetrics,
  AblationResult, CurveData, PerClassMetrics,
} from './types';

export const mlAnalyticsApi = {
  getPerformanceMetrics: (params: {
    modelVersion?: string;
    from?: number;
    to?: number;
    granularity?: 'minute' | 'hour' | 'day';
  }) =>
    api.get<ModelPerformanceMetrics[]>('/v1/ml/performance', { params }).then((r) => r.data),
  
  getLatestPerformance: (modelVersion: string) =>
    api.get<ModelPerformanceMetrics>(`/v1/ml/performance/${modelVersion}/latest`).then((r) => r.data),
  
  getPerClassMetrics: (modelVersion: string, datasetVersion?: string) =>
    api.get<PerClassMetrics[]>(`/v1/ml/performance/${modelVersion}/per-class`, {
      params: { datasetVersion },
    }).then((r) => r.data),
  
  getConfusionMatrix: (modelVersion: string, normalized = true) =>
    api.get<ConfusionMatrix>(`/v1/ml/performance/${modelVersion}/confusion-matrix`, {
      params: { normalized },
    }).then((r) => r.data),
  
  getROCCurve: (modelVersion: string, className: string) =>
    api.get<CurveData>(`/v1/ml/curves/${modelVersion}/roc`, { params: { class: className } }).then((r) => r.data),
  
  getPRCurve: (modelVersion: string, className: string) =>
    api.get<CurveData>(`/v1/ml/curves/${modelVersion}/pr`, { params: { class: className } }).then((r) => r.data),
  
  getCalibration: (modelVersion: string) =>
    api.get<CalibrationData>(`/v1/ml/performance/${modelVersion}/calibration`).then((r) => r.data),
  
  getDataDrift: (params: {
    referenceWindow: { start: number; end: number };
    testWindow: { start: number; end: number };
    method?: 'ks_test' | 'psi' | 'js_divergence';
  }) =>
    api.post<DriftReport>('/v1/ml/drift/data', params).then((r) => r.data),
  
  getConceptDrift: (modelVersion: string, method?: string) =>
    api.get<ConceptDriftReport>(`/v1/ml/drift/concept/${modelVersion}`, { params: { method } }).then((r) => r.data),
  
  getFeatureImportance: (modelVersion: string) =>
    api.get<Array<{ feature: string; importance: number }>>(
      `/v1/ml/feature-importance/${modelVersion}`
    ).then((r) => r.data),
  
  getFairnessMetrics: (modelVersion: string, protectedAttribute: string) =>
    api.get<FairnessMetrics>(`/v1/ml/fairness/${modelVersion}`, {
      params: { attribute: protectedAttribute },
    }).then((r) => r.data),
  
  getAblationResults: (experimentId: string) =>
    api.get<AblationResult[]>(`/v1/ml/ablation/${experimentId}`).then((r) => r.data),
  
  compareModels: (versions: string[]) =>
    api.post<ModelPerformanceMetrics[]>('/v1/ml/compare', { versions }).then((r) => r.data),
};
