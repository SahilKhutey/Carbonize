/**
 * Mock API Server for Development
 * Run: npx tsx src/mock/server.ts
 */
import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';

const app = express();
app.use(cors());
app.use(express.json());

const state = {
  simState: {
    status: 'running' as 'running' | 'paused' | 'idle' | 'error',
    currentTime: 0,
    realTime: 0,
    speedFactor: 1.0,
    environment: {
      co2Level: 0.5,
      co2Concentration: 420,
      temperature: 22,
      humidity: 50,
      lightIntensity: 1.0,
      windSpeed: 2,
    },
    fog: { enabled: false, density: 0 },
    robots: [],
    scenarios: [],
  },
  robots: new Map<string, any>(),
  detections: [] as any[],
  alerts: [] as any[],
  models: [
    { id: '1', name: 'yolov8n-carbonize', version: '1.5.0', stage: 'Production', format: 'engine', size: 14_500_000, metrics: { mAP50: 0.89, mAP50_95: 0.67, precision: 0.85, recall: 0.82, latencyMs: 18.5 }, trafficPercent: 100, registeredAt: new Date().toISOString() },
    { id: '2', name: 'yolov11n-carbonize', version: '0.3.0', stage: 'Staging', format: 'engine', size: 16_200_000, metrics: { mAP50: 0.92, mAP50_95: 0.71, precision: 0.88, recall: 0.85, latencyMs: 22.3 }, trafficPercent: 0, registeredAt: new Date().toISOString() },
  ],
  experiments: [
    {
      id: 'exp1', name: 'YOLOv8 vs YOLOv11', description: 'Comparing latest model architectures',
      status: 'running',
      variants: [
        { name: 'v8', modelId: '1', trafficWeight: 0.5, isControl: true, samples: 4521, metrics: { avgLatencyMs: 18.5, avgConfidence: 0.85, successRate: 0.97 } },
        { name: 'v11', modelId: '2', trafficWeight: 0.5, isControl: false, samples: 4498, metrics: { avgLatencyMs: 22.3, avgConfidence: 0.88, successRate: 0.98 } },
      ],
    },
  ],
};

for (let i = 0; i < 3; i++) {
  const id = `robot_${i + 1}`;
  state.robots.set(id, {
    id, name: `Carbon-Bot ${i + 1}`,
    status: ['idle', 'navigating', 'capturing'][i] as any,
    battery: 75 + Math.random() * 25,
    position: { x: (Math.random() - 0.5) * 10, y: 0, z: (Math.random() - 0.5) * 10 },
    pose: { position: [0, 0, 0], orientation: [0, 0, 0, 1] },
    lastSeen: new Date().toISOString(),
  });
}

function simulateRobotMotion() {
  state.robots.forEach((r) => {
    if (r.status === 'navigating') {
      r.position.x += (Math.random() - 0.5) * 0.1;
      r.position.z += (Math.random() - 0.5) * 0.1;
      r.battery = Math.max(0, r.battery - 0.02);
    }
  });
}

function simulateCO2() {
  state.simState.environment.co2Concentration = 400 + Math.sin(Date.now() / 5000) * 100 + Math.random() * 20;
  state.simState.currentTime += state.simState.speedFactor * 0.1;
}

function simulateDetection() {
  if (Math.random() < 0.3) {
    const robot = Array.from(state.robots.values())[Math.floor(Math.random() * 3)];
    const det = {
      id: `det_${Date.now()}_${Math.random()}`,
      timestamp: Date.now(),
      robotId: robot.id,
      class: ['co2_emitter', 'capture_unit', 'industrial_equipment'][Math.floor(Math.random() * 3)],
      confidence: 0.7 + Math.random() * 0.3,
      bbox: [Math.random() * 100, Math.random() * 100, 200 + Math.random() * 200, 200 + Math.random() * 200] as [number, number, number, number],
      imageUrl: `https://picsum.photos/640/480?random=${Math.random()}`,
      modelVersion: '1.5.0',
      position: { x: robot.position.x, y: robot.position.y + 0.5, z: robot.position.z },
    };
    state.detections.unshift(det);
    if (state.detections.length > 500) state.detections.pop();
    broadcast({ type: 'detection', data: det });
  }
}

function simulateAlert() {
  if (Math.random() < 0.05) {
    const alert = {
      id: `alert_${Date.now()}`,
      type: ['co2_high', 'battery_low', 'latency_high'][Math.floor(Math.random() * 3)],
      severity: ['warning', 'error'][Math.floor(Math.random() * 2)] as any,
      message: 'Simulated alert for testing',
      timestamp: Date.now(),
      acknowledged: false,
    };
    state.alerts.unshift(alert);
    broadcast({ type: 'alert', data: alert });
  }
}

app.get('/v1/health/ready', (_, res) => res.json({ status: 'ready', checks: {} }));
app.get('/v1/robots', (_, res) => res.json(Array.from(state.robots.values())));
app.get('/v1/detections', (req, res) => {
  const limit = parseInt((req.query.limit as string) || '100');
  res.json(state.detections.slice(0, limit));
});
app.get('/v1/models', (_, res) => res.json(state.models));
app.get('/v1/simulation/state', (_, res) => res.json(state.simState));
app.post('/v1/simulation/start', (_, res) => { state.simState.status = 'running'; res.json({ status: 'started' }); });
app.post('/v1/simulation/pause', (_, res) => { state.simState.status = 'paused'; res.json({}); });
app.post('/v1/simulation/resume', (_, res) => { state.simState.status = 'running'; res.json({}); });
app.post('/v1/simulation/stop', (_, res) => { state.simState.status = 'idle'; res.json({}); });
app.post('/v1/simulation/step', (_, res) => res.json({}));
app.get('/v1/experiments', (_, res) => res.json(state.experiments));
app.get('/v1/alerts', (_, res) => res.json(state.alerts));

app.get('/v1/ml/performance', (_, res) => {
  const data = Array.from({ length: 96 }, (_, i) => ({
    timestamp: Date.now() - (96 - i) * 900_000,
    modelVersion: '1.5.0',
    mAP50: 0.88 + Math.sin(i / 10) * 0.03,
    mAP75: 0.78 + Math.sin(i / 10) * 0.03,
    mAP50_95: 0.65 + Math.sin(i / 10) * 0.02,
    precision: 0.85 + Math.cos(i / 12) * 0.03,
    recall: 0.82 + Math.sin(i / 8) * 0.03,
    f1Score: 0.835,
    accuracy: 0.91,
    inferenceLatencyMs: 18 + Math.random() * 4,
    throughputFps: 52 + Math.random() * 5,
    gpuUtilization: 65 + Math.random() * 20,
    memoryUsageMb: 1024 + Math.random() * 100,
  }));
  res.json(data);
});

app.get('/v1/ml/performance/:modelVersion/latest', (_, res) => {
  res.json({
    timestamp: Date.now(),
    modelVersion: '1.5.0',
    mAP50: 0.89, mAP75: 0.79, mAP50_95: 0.67, precision: 0.86, recall: 0.83, f1Score: 0.845, accuracy: 0.92,
    inferenceLatencyMs: 18.5, throughputFps: 54.0, gpuUtilization: 72, memoryUsageMb: 1080,
  });
});

app.get('/v1/ml/performance/:modelVersion/per-class', (_, res) => {
  const classes = ['co2_emitter', 'capture_unit', 'industrial_equipment', 'pipeline', 'valve', 'tank'];
  res.json(classes.map((cls) => ({
    className: cls,
    precision: 0.8 + Math.random() * 0.15,
    recall: 0.75 + Math.random() * 0.2,
    f1Score: 0.78 + Math.random() * 0.15,
    support: 1000 + Math.floor(Math.random() * 500),
    tp: 800, fp: 120, fn: 80, averagePrecision: 0.85, confidenceHistogram: [10, 20, 30, 50, 100, 150, 200, 300, 400, 500],
  })));
});

app.get('/v1/ml/performance/:modelVersion/confusion-matrix', (_, res) => {
  const classes = ['co2_emitter', 'capture_unit', 'industrial_equipment', 'pipeline', 'valve', 'tank'];
  const n = classes.length;
  const matrix = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 850 : Math.floor(Math.random() * 20)))
  );
  const normalized = matrix.map((row) => {
    const sum = row.reduce((a, b) => a + b, 0);
    return row.map((v) => v / sum);
  });
  res.json({ classes, matrix, normalized });
});

app.get('/v1/ml/performance/:modelVersion/calibration', (_, res) => {
  const bins = Array.from({ length: 10 }, (_, i) => {
    const binCenter = (i + 0.5) / 10;
    return {
      binCenter, averageConfidence: binCenter, actualAccuracy: binCenter + (Math.random() - 0.5) * 0.08,
      count: 150, gap: (Math.random() - 0.5) * 0.08,
    };
  });
  res.json({ bins, expectedCalibrationError: 0.034, maximumCalibrationError: 0.078, brierScore: 0.092 });
});

app.post('/v1/ml/drift/data', (_, res) => {
  const features = ['brightness', 'contrast', 'saturation', 'edge_density', 'noise_level', 'size_avg', 'aspect_ratio']
    .map((name) => {
      const score = Math.random();
      return {
        name, driftScore: score, pValue: score > 0.7 ? 0.02 : 0.4, threshold: 0.7, isDrifted: score > 0.7,
        statistic: score * 0.4,
        referenceDistribution: Array.from({ length: 20 }, () => Math.random()),
        testDistribution: Array.from({ length: 20 }, () => Math.random() * (score > 0.7 ? 1.2 : 1.0)),
      };
    });
  res.json({
    timestamp: Date.now(), detection: 'no_drift', overallScore: 0.14, features, method: 'ks_test',
    referenceWindow: { start: Date.now() - 7 * 86400000, end: Date.now() - 86400000 },
    testWindow: { start: Date.now() - 86400000, end: Date.now() },
  });
});

app.get('/v1/ml/drift/concept/:modelVersion', (_, res) => {
  res.json({ timestamp: Date.now(), detection: 'no_drift', errorRate: 0.07, baselineErrorRate: 0.05, driftMagnitude: 0.12, method: 'eddm' });
});

app.get('/v1/ml/fairness/:modelVersion', (_, res) => {
  const groups = ['lighting_low', 'lighting_high', 'weather_clear', 'weather_foggy']
    .map((name) => ({ groupName: name, size: 1200, positiveRate: 0.45, truePositiveRate: 0.82, falsePositiveRate: 0.04, precision: 0.86 }));
  res.json({
    timestamp: Date.now(), protectedAttribute: 'environment_condition', groups,
    metrics: { demographicParity: 0.042, equalizedOdds: 0.038, equalOpportunity: 0.025, predictiveParity: 0.031 },
  });
});

app.get('/v1/ml/ablation/:experimentId', (_, res) => {
  res.json([
    { configName: 'Full (v1.5.0)', metrics: { mAP50: 0.89, mAP50_95: 0.67, latencyMs: 18.5 }, features: { backbone: true, fpn: true, data_aug: true, multi_scale: true, attention: true }, trainingDurationMin: 120, modelSizeMb: 14.5 },
    { configName: 'No Attention', metrics: { mAP50: 0.85, mAP50_95: 0.63, latencyMs: 15.2 }, features: { backbone: true, fpn: true, data_aug: true, multi_scale: true, attention: false }, trainingDurationMin: 95, modelSizeMb: 12.8 },
    { configName: 'No Multi-Scale', metrics: { mAP50: 0.82, mAP50_95: 0.59, latencyMs: 14.1 }, features: { backbone: true, fpn: true, data_aug: true, multi_scale: false, attention: true }, trainingDurationMin: 80, modelSizeMb: 14.5 },
    { configName: 'No Augmentation', metrics: { mAP50: 0.78, mAP50_95: 0.54, latencyMs: 18.5 }, features: { backbone: true, fpn: true, data_aug: false, multi_scale: true, attention: true }, trainingDurationMin: 60, modelSizeMb: 14.5 },
  ]);
});

app.post('/v1/inference/predict', (_, res) => {
  res.json({
    request_id: 'req-' + Date.now(),
    model_version: '1.5.0',
    detections: [
      { x_min: 50, y_min: 50, x_max: 200, y_max: 200, confidence: 0.94, class_id: 0, class_name: 'co2_emitter' },
      { x_min: 250, y_min: 100, x_max: 400, y_max: 300, confidence: 0.88, class_id: 1, class_name: 'capture_unit' },
    ],
    inference_time_ms: 18.5,
    preprocessing_ms: 2.1,
    postprocessing_ms: 1.4,
    image_dimensions: { width: 640, height: 480 },
  });
});

app.post('/v1/tests/runs', (_, res) => {
  res.status(201).json({
    id: 'run-' + Date.now(),
    name: 'Batch Test Run',
    model_id: '1.5.0',
    test_type: 'batch',
    status: 'completed',
    progress: 1.0,
    total_samples: 100,
    processed_samples: 100,
    failed_samples: 0,
    metrics: { mAP50: 0.892, precision: 0.865, recall: 0.834, avgInferenceMs: 18.5 },
    confusion_matrix: {
      classes: ['co2_emitter', 'capture_unit', 'equipment', 'pipeline', 'valve', 'tank'],
      matrix: [
        [850, 20, 15, 10, 3, 2], [18, 890, 12, 5, 2, 3], [12, 15, 870, 20, 5, 8],
        [8, 10, 15, 910, 10, 2], [5, 4, 8, 12, 860, 15], [3, 5, 10, 5, 12, 880],
      ],
    },
    created_at: new Date().toISOString(),
  });
});

app.get('/v1/tests/runs/:id', (req, res) => {
  res.json({
    id: req.params.id,
    name: 'Batch Test Run',
    model_id: '1.5.0',
    test_type: 'batch',
    status: 'completed',
    progress: 1.0,
    total_samples: 100,
    processed_samples: 100,
    failed_samples: 0,
    metrics: { mAP50: 0.892, precision: 0.865, recall: 0.834, avgInferenceMs: 18.5 },
    confusion_matrix: {
      classes: ['co2_emitter', 'capture_unit', 'equipment', 'pipeline', 'valve', 'tank'],
      matrix: [
        [850, 20, 15, 10, 3, 2], [18, 890, 12, 5, 2, 3], [12, 15, 870, 20, 5, 8],
        [8, 10, 15, 910, 10, 2], [5, 4, 8, 12, 860, 15], [3, 5, 10, 5, 12, 880],
      ],
    },
    created_at: new Date().toISOString(),
  });
});

app.post('/v1/tests/ab-test', (_, res) => {
  res.json({ test_run_id: 'ab-run-' + Date.now(), status: 'queued' });
});

app.get('/v1/predictions', (_, res) => {
  res.json([
    {
      id: 'pred-1',
      name: 'CO₂ Capture Rate 24h Forecast',
      metric_type: 'co2_capture',
      forecast_model: 'prophet',
      horizon_hours: 24,
      status: 'completed',
      forecast_points: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() + (i + 1) * 3600_000).toISOString(),
        predicted_value: 120 + Math.sin(i / 4) * 20,
        lower_bound: 108 + Math.sin(i / 4) * 18,
        upper_bound: 132 + Math.sin(i / 4) * 22,
        confidence: 0.95,
      })),
      anomalies: [
        { timestamp: new Date(Date.now() - 4 * 3600_000).toISOString(), value: 165.4, anomaly_score: 0.88, is_anomaly: true, threshold: 0.7, severity: 'high' },
      ],
      confidence_level: 0.95,
      training_metrics: { mape: 3.42, rmse: 1.85, mae: 1.42 },
      created_at: new Date().toISOString(),
    },
  ]);
});

app.post('/v1/predictions', (req, res) => {
  const body = req.body || {};
  res.status(201).json({
    id: 'pred-' + Date.now(),
    name: body.name || 'New Forecast',
    metric_type: body.metric_type || 'co2_capture',
    forecast_model: body.forecast_model || 'prophet',
    horizon_hours: body.horizon_hours || 24,
    status: 'completed',
    forecast_points: Array.from({ length: body.horizon_hours || 24 }, (_, i) => ({
      timestamp: new Date(Date.now() + (i + 1) * 3600_000).toISOString(),
      predicted_value: 120 + Math.sin(i / 4) * 20,
      lower_bound: 108 + Math.sin(i / 4) * 18,
      upper_bound: 132 + Math.sin(i / 4) * 22,
      confidence: 0.95,
    })),
    anomalies: [],
    confidence_level: 0.95,
    training_metrics: { mape: 3.42, rmse: 1.85, mae: 1.42 },
    created_at: new Date().toISOString(),
  });
});

app.get('/v1/predictions/:id', (req, res) => {
  res.json({
    id: req.params.id,
    name: 'CO₂ Capture Rate 24h Forecast',
    metric_type: 'co2_capture',
    forecast_model: 'prophet',
    horizon_hours: 24,
    status: 'completed',
    forecast_points: Array.from({ length: 24 }, (_, i) => ({
      timestamp: new Date(Date.now() + (i + 1) * 3600_000).toISOString(),
      predicted_value: 120 + Math.sin(i / 4) * 20,
      lower_bound: 108 + Math.sin(i / 4) * 18,
      upper_bound: 132 + Math.sin(i / 4) * 22,
      confidence: 0.95,
    })),
    anomalies: [
      { timestamp: new Date(Date.now() - 4 * 3600_000).toISOString(), value: 165.4, anomaly_score: 0.88, is_anomaly: true, threshold: 0.7, severity: 'high' },
    ],
    confidence_level: 0.95,
    training_metrics: { mape: 3.42, rmse: 1.85, mae: 1.42 },
    created_at: new Date().toISOString(),
  });
});

app.post('/v1/predictions/what-if', (_, res) => {
  res.json({
    base_forecast: [],
    modified_forecast: [],
    delta: [],
    impact_summary: { avg_percent_change: 15.0, max_increase: 18.2, max_decrease: -1.2, total_change: 180.5 },
  });
});

app.get('/v1/drift/state', (_, res) => {
  res.json({
    data_drift: {
      co2_ppm_robot_1: {
        history: [
          { timestamp: Date.now() - 3600000, overall_drifted: false, overall_score: 0.04, recommendation: 'continue' },
          { timestamp: Date.now() - 1800000, overall_drifted: true, overall_score: 0.32, recommendation: 'trigger_warning' },
        ],
      },
      temperature_robot_1: {
        history: [
          { timestamp: Date.now() - 3600000, overall_drifted: false, overall_score: 0.01, recommendation: 'continue' },
        ],
      },
    },
    concept_drift: {
      '1.5.0': { current_error_rate: 0.04, drift_detected: false },
      '1.4.0': { current_error_rate: 0.28, drift_detected: true },
    },
  });
});

app.get('/v1/drift/history', (_, res) => {
  res.json([]);
});

app.post('/v1/drift/detect', (_, res) => {
  res.json({
    timestamp: Date.now(),
    overall_drifted: true,
    overall_score: 0.28,
    n_features_drifted: 1,
    n_features: 2,
    recommended_action: 'trigger_warning',
    results: [
      { feature: 'co2_ppm', method: 'ks_test', is_drifted: true, score: 0.28, threshold: 0.05, statistic: 0.28, p_value: 0.001, confidence: 0.999 },
    ],
  });
});

app.post('/v1/drift/reset', (req, res) => {
  res.json({ status: 'reset', metric_key: req.body?.metric_key || 'co2_ppm_robot_1' });
});

app.get('/v1/gameday/list', (_, res) => {
  res.json([
    { id: 'gd_2024_q1_001', name: 'Q1 2024 — Database Failover Drill', date: '2024-03-15', duration_minutes: 120, participants: 4, injects: 2 },
    { id: 'gd_2024_q1_002', name: 'Q1 2024 — Kafka Broker Failure', date: '2024-03-22', duration_minutes: 90, participants: 3, injects: 1 },
  ]);
});

app.post('/v1/gameday/:id/run', (req, res) => {
  res.json({ status: 'running', gameday_id: req.params.id, meeting_link: 'https://meet.carbonize.io/gameday' });
});

app.get('/v1/gameday/:id/status', (req, res) => {
  res.json({
    id: req.params.id,
    name: 'Database Failover Drill',
    current_phase: 'triage',
    started_at: Date.now() - 600000,
    completed_at: null,
    injects_completed: 1,
    injects_total: 2,
  });
});

app.post('/v1/gameday/:id/action', (_, res) => {
  res.json({ status: 'recorded' });
});

app.post('/v1/chemistry/vle/equilibrium', (req, res) => {
  const loading = req.body?.loading || 0.5;
  const p = 1420 * Math.pow(loading / 0.5, 2.1);
  res.json({
    amine: req.body?.amine || 'MEA',
    T: req.body?.T || 313.15,
    loading,
    P_CO2_pa: p,
    henry_constant: p / (loading * loading),
  });
});

app.post('/v1/chemistry/pollutants/sox', (req, res) => {
  const so2 = req.body?.SO2_in_ppm || 800;
  res.json({
    SO2_in: so2,
    SO2_out: so2 * 0.045,
    efficiency: 95.5,
    limestone_consumed_kg_h: so2 * 0.15,
    gypsum_produced_kg_h: so2 * 0.21,
  });
});

app.post('/v1/chemistry/pollutants/nox', (req, res) => {
  const no = req.body?.NO_in_ppm || 300;
  res.json({
    NO_in: no,
    NO_out: no * 0.075,
    efficiency: 92.5,
    ammonia_slip_ppm: 2.1,
  });
});

app.post('/v1/chemistry/pollutants/mercury', (req, res) => {
  const hg = req.body?.Hg_in_ug_Nm3 || 15.0;
  res.json({
    Hg_in: hg,
    Hg_out: hg * 0.09,
    efficiency: 91.0,
    sorbent_consumed_kg_h: 4.5,
  });
});

app.post('/v1/chemistry/plant/simulate', (_, res) => {
  res.json({
    snapshots: Array.from({ length: 10 }, (_, i) => ({
      timestamp: Date.now() - (10 - i) * 60000,
      CO2_capture_efficiency: 91.2 + Math.random() * 2,
      CO2_capture_rate: 4500 + Math.random() * 100,
      reboiler_duty: 3.45 + Math.random() * 0.1,
    })),
    final_efficiency: 92.4,
  });
});

app.post('/v1/reactor/solve', (req, res) => {
  const len = req.body?.length || 2.0;
  const n = 50;
  const z = Array.from({ length: n }, (_, i) => (i * len) / (n - 1));
  const co = z.map((zVal) => 0.05 * Math.exp(-0.8 * zVal));
  const co2 = z.map((zVal) => 0.05 * (1 - Math.exp(-0.8 * zVal)));
  res.json({
    z,
    profiles: { CO: co, CO2: co2 },
    T_profile: z.map((zVal) => 573.15 + 15 * Math.sin((zVal / len) * Math.PI)),
    P_profile: z.map((zVal) => 200000 - zVal * 700),
    conversion: { CO: 78.4 },
    pressure_drop: 1420,
    ghsv: 3600,
    space_time: 0.42,
  });
});

app.get('/v1/reactor/thiele', (req, res) => {
  const r = Number(req.query.r) || 0.0015;
  const k = Number(req.query.k) || 10.0;
  const D = Number(req.query.D_eff) || 1e-6;
  const phi = r * Math.sqrt(k / D);
  const eta = phi < 0.1 ? 1.0 : (3.0 / phi) * (1.0 / Math.tanh(phi) - 1.0 / phi);
  res.json({ phi, eta });
});

app.post('/api/v1/lab/molecular/solvent/design', (req, res) => {
  const amine = req.body?.amine_type || 'primary';
  res.json({
    candidates: [
      { name: `COSMO-Solvent-${amine}-1`, CO2_loading_max: 0.52, cyclic_capacity: 0.41, regeneration_energy: 42.5, overall_score: 88.4, toxicity: 2200, cost: 3.5 },
      { name: `COSMO-Solvent-${amine}-2`, CO2_loading_max: 0.48, cyclic_capacity: 0.38, regeneration_energy: 39.0, overall_score: 82.1, toxicity: 3100, cost: 2.8 },
      { name: `COSMO-Solvent-${amine}-3`, CO2_loading_max: 0.55, cyclic_capacity: 0.44, regeneration_energy: 45.0, overall_score: 79.5, toxicity: 1800, cost: 4.2 },
    ],
  });
});

app.post('/api/v1/lab/doe/design', (req, res) => {
  const type = req.body?.design_type || 'full_factorial';
  const runs = [
    [313, 100000, 0.1],
    [353, 100000, 0.1],
    [313, 500000, 0.1],
    [353, 500000, 0.1],
    [313, 100000, 0.5],
    [353, 100000, 0.5],
    [313, 500000, 0.5],
    [353, 500000, 0.5],
  ];
  res.json({ design_type: type, n_runs: runs.length, design: runs });
});

app.post('/api/v1/lab/safety/hazop/run', (_, res) => {
  res.json({
    unit: 'CO2_Absorber_Column',
    nodes: [
      { parameter: 'temperature', deviation: 'high', causes: ['Heat exchanger failure'], consequences: ['Amine degradation'], safeguards: ['Temperature alarms'], risk: 'medium' },
      { parameter: 'solvent_flow', deviation: 'low', causes: ['Pump blockage'], consequences: ['Reduced capture efficiency'], safeguards: ['Low flow trip'], risk: 'medium' },
      { parameter: 'CO2_pressure', deviation: 'high', causes: ['Downstream valve closure'], consequences: ['Vessel overpressure'], safeguards: ['PSV relief valve'], risk: 'low' },
    ],
  });
});

app.post('/api/v1/lab/discovery/hypotheses/generate', (_, res) => {
  res.json({
    hypotheses: [
      { id: 'h1', statement: 'Increasing sterically hindered group size reduces heat of absorption by 15%', rationale: 'Shielded carbamate formation lowers binding enthalpy', confidence: 0.84 },
      { id: 'h2', statement: 'Sulfur-impregnated activated carbon increases trace Hg capture efficiency to 98%', rationale: 'Strong chemisorption via Hg-S complexation', confidence: 0.91 },
    ],
  });
});

app.post('/api/v1/compchem/md/run', (req, res) => {
  const steps = req.body?.n_steps || 200;
  const energies = Array.from({ length: 8 }, (_, i) => ({
    step: i * 25,
    time: i * 0.025,
    KE: 145.2 + Math.random() * 5,
    PE: -542.1 + Math.random() * 8,
    total: -396.9,
    T: 300.0 + Math.random() * 3 - 1.5,
  }));
  res.json({ energies, mean_T: 300.2, diffusion_coefficients: { MEA: 1.25e-5 } });
});

app.post('/api/v1/compchem/qc/:method', (req, res) => {
  const method = req.params.method || 'dft';
  res.json({
    energy: method === 'dft' ? -76.42518 : -75.89124,
    energy_au: method === 'dft' ? -76.42518 : -75.89124,
    converged: true,
    iterations: 8,
    dipole_moment: [0.0, 0.0, 1.85],
    solvation_energy: -9.45,
  });
});

app.post('/api/v1/compchem/materials/crystal', (req, res) => {
  const type = req.body?.structure_type || 'rock_salt';
  res.json({
    name: `Crystal_${type}`,
    lattice: [[4.0, 0, 0], [0, 4.0, 0], [0, 0, 4.0]],
    volume: 64.0,
    basis: [
      { element: 'Na', position: [0, 0, 0] },
      { element: 'Cl', position: [0.5, 0.5, 0.5] },
    ],
  });
});

app.post('/api/v1/compchem/materials/phase-diagram', (_, res) => {
  res.json({
    temperatures: [300, 600, 900, 1200, 1500, 1800],
    mole_fractions: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    phase_names: ['FCC', 'LIQUID'],
  });
});

app.post('/api/v1/ssml/band-structure', (req, res) => {
  const func = req.body?.functional || 'LDA';
  const gap = func === 'HSE06' ? 1.42 : (func === 'PBE' ? 1.15 : 1.05);
  res.json({
    k_distances: [0.0, 1.0, 2.0, 3.0],
    k_positions: [0.0, 1.0, 2.0, 3.0],
    labels: ['Γ', 'X', 'M', 'Γ'],
    bands: Array.from({ length: 4 }, () => [2.0, 3.0, 4.2 + gap, 6.0]),
    efermi: 4.2,
    gap_info: { gap, vbm: 3.5, cbm: 3.5 + gap, direct: true, type: 'semiconductor' },
  });
});

app.post('/api/v1/ssml/dos', (_, res) => {
  res.json({
    energies: Array.from({ length: 20 }, (_, i) => -5 + i * 0.75),
    dos: Array.from({ length: 20 }, () => Math.random() * 10 + 2),
    efermi: 4.2,
  });
});

app.post('/api/v1/ssml/phonons', (_, res) => {
  res.json({
    k_distances: [0.0, 1.0, 2.0, 3.0],
    bands: Array.from({ length: 4 }, () => [5.0, 8.0, 12.0, 15.0, 18.0, 22.4]),
  });
});

app.post('/api/v1/ssml/transport', (_, res) => {
  res.json({
    mu: [3.0, 3.5, 4.0, 4.5, 5.0],
    sigma: [1.2e5, 1.4e5, 1.5e5, 1.3e5, 1.1e5],
    seebeck: [-120, -150, -185.4, -160, -130],
    kappa_e: [0.8, 1.0, 1.2, 1.1, 0.9],
    power_factor: [2.1, 2.8, 3.4, 2.9, 2.2],
    ZT: [0.95, 1.25, 1.45, 1.30, 1.05],
  });
});

app.post('/api/v1/ssml/active-learning/run', (req, res) => {
  const iters = req.body?.n_iterations || 5;
  const history = Array.from({ length: iters }, (_, i) => ({
    iteration: i + 1,
    n_labeled: (i + 1) * 10,
    avg_uncertainty: 0.12 / Math.sqrt(i + 1),
    max_uncertainty: 0.18 / Math.sqrt(i + 1),
  }));
  res.json({ history });
});










const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws/telemetry' });

wss.on('connection', (ws) => {
  console.log('Client connected');
  ws.on('close', () => console.log('Client disconnected'));
});

function broadcast(msg: any) {
  wss.clients.forEach((client) => {
    if (client.readyState === 1) {
      client.send(JSON.stringify(msg));
    }
  });
}

setInterval(() => {
  simulateRobotMotion();
  simulateCO2();
  simulateDetection();
  simulateAlert();
  broadcast({ type: 'sim_state', data: { ...state.simState, robots: Array.from(state.robots.values()) } });
}, 1000);

const PORT = 8000;
server.listen(PORT, () => {
  console.log(`🚀 Mock API server running on http://localhost:${PORT}`);
  console.log(`   WebSocket: ws://localhost:${PORT}/ws/telemetry`);
});
