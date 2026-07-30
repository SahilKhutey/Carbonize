import { api } from '@/lib/api';
import type { TestConfig, TestRunResults, ABTestComparison, TestSample } from './types';

export const testingApi = {
  predictSingle: async (modelId: string, imageFile: File, config: TestConfig) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('model_id', modelId);
    formData.append('confidence_threshold', config.confidenceThreshold.toString());
    formData.append('iou_threshold', config.iouThreshold.toString());
    formData.append('max_detections', config.maxDetections.toString());
    
    if (config.edgeSimulator) {
      formData.append('edge_simulator', JSON.stringify(config.edgeSimulator));
    }
    
    return api.post('/v1/inference/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data);
  },
  
  predictAsync: async (modelId: string, imageFile: File, config: TestConfig) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('model_id', modelId);
    formData.append('confidence_threshold', config.confidenceThreshold.toString());
    formData.append('iou_threshold', config.iouThreshold.toString());
    
    return api.post('/v1/inference/predict-async', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data);
  },
  
  getAsyncTask: (taskId: string) =>
    api.get(`/v1/inference/task/${taskId}`).then((r) => r.data),
  
  createTestRun: (data: any) =>
    api.post('/v1/tests/runs', data).then((r) => r.data),
  
  getTestRun: (runId: string) =>
    api.get(`/v1/tests/runs/${runId}`).then((r) => r.data),
  
  getTestPredictions: (runId: string, limit = 100) =>
    api.get(`/v1/tests/runs/${runId}/predictions`, { params: { limit } })
       .then((r) => r.data),
  
  cancelTestRun: (runId: string) =>
    api.post(`/v1/tests/runs/${runId}/cancel`).then((r) => r.data),
  
  createABTest: (modelAId: string, modelBId: string, datasetId: string) =>
    api.post('/v1/tests/ab-test', { modelAId, modelBId, datasetId })
       .then((r) => r.data),
  
  startTuning: (modelId: string, searchSpace: any, trials: number) =>
    api.post('/v1/tests/tuning', { modelId, searchSpace, trials }).then((r) => r.data),
  
  getTuningResults: (tuningId: string) =>
    api.get(`/v1/tests/tuning/${tuningId}`).then((r) => r.data),
};
