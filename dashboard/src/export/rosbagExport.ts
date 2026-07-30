import { saveAs } from 'file-saver';

export interface BagMessage {
  topic: string;
  timestamp: number;
  data: any;
  type: string;
}

export interface RosbagExportConfig {
  messages: BagMessage[];
  topics: Array<{ name: string; type: string }>;
  startTime: number;
  endTime: number;
  metadata?: Record<string, string>;
  filename: string;
}

export async function exportAsRosbag(config: RosbagExportConfig): Promise<Blob> {
  const response = await fetch('/api/v1/export/rosbag', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  
  if (!response.ok) {
    return exportAsJsonl(config.messages, config.filename);
  }
  
  const blob = await response.blob();
  saveAs(blob, `${config.filename}.mcap`);
  return blob;
}

export function exportAsJsonl(messages: BagMessage[], filename: string): Blob {
  const jsonl = messages.map((m) => JSON.stringify(m)).join('\n');
  const blob = new Blob([jsonl], { type: 'application/x-ndjson' });
  saveAs(blob, `${filename}.jsonl`);
  return blob;
}
