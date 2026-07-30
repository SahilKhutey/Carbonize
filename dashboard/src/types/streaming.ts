export interface StreamSubscription {
  robot_id: string | null;
  metric_types: string[];
  classes: string[];
  min_severity: 'info' | 'warning' | 'error' | 'critical';
  model_version?: string;
  bounding_box?: { x_min: number; y_min: number; x_max: number; y_max: number } | null;
}

export interface WSMessage {
  type: 'welcome' | 'telemetry' | 'detection' | 'alert' | 'anomaly' | 'aggregate' | 'drift' | 'drift_summary' | 'subscribe_ack' | 'pong' | 'stats' | 'heartbeat' | 'error';
  data?: any;
  subscription?: StreamSubscription;
  timestamp?: number;
  client_id?: string;
  server_time?: number;
  protocol_version?: string;
  message?: string;
}
