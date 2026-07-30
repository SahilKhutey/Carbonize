export type ExportFormat = 'pdf' | 'png' | 'svg' | 'csv' | 'json' | 'xlsx' | 'parquet' | 'rosbag' | 'jsonl';

export interface ExportOptions {
  format: ExportFormat;
  filename: string;
  title?: string;
  includeCharts?: boolean;
  includeRawData?: boolean;
  includeMetadata?: boolean;
  dateRange?: { start: number; end: number };
  filters?: Record<string, any>;
}

export interface ExportProgress {
  format: ExportFormat;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  url?: string;
  size?: number;
}
