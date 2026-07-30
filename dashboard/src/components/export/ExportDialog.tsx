import { useState } from 'react';
import { FileText, Image, FileSpreadsheet, FileJson, Package } from 'lucide-react';
import { exportAsCSV, exportAsJSON, exportAsExcel, exportMultiSheetExcel } from '@/export/dataExport';
import { exportChartAsPNG, exportChartAsSVG, exportChartsAsPDF } from '@/export/chartExport';
import { exportAsRosbag, exportAsJsonl } from '@/export/rosbagExport';
import { Modal } from '@/components/ui/Modal';
import { cn } from '@/lib/utils';

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
  data?: any[];
  charts?: Array<{ title: string; element: HTMLElement }>;
  filename?: string;
  title?: string;
  rosbagData?: any;
  metadata?: Record<string, any>;
}

export function ExportDialog({ open, onClose, data, charts, filename = 'carbonize_export', title, rosbagData, metadata }: ExportDialogProps) {
  const [exporting, setExporting] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  
  const exportFormats = [
    { id: 'pdf', label: 'PDF Report', icon: FileText, description: 'Formatted PDF with embedded charts' },
    { id: 'png', label: 'PNG (high-DPI)', icon: Image, description: 'Chart images at 3x resolution' },
    { id: 'svg', label: 'SVG Vector', icon: Image, description: 'Scalable vector graphics' },
    { id: 'csv', label: 'CSV Data', icon: FileSpreadsheet, description: 'Spreadsheet raw tabular data' },
    { id: 'json', label: 'JSON Data', icon: FileJson, description: 'Structured JSON payload' },
    { id: 'xlsx', label: 'Excel Workbook', icon: FileSpreadsheet, description: 'Multi-sheet .xlsx workbook' },
    { id: 'rosbag', label: 'ROS Bag (MCAP)', icon: Package, description: 'Replayable MCAP telemetry bag' },
    { id: 'jsonl', label: 'JSON Lines', icon: FileJson, description: 'Streaming NDJSON format' },
  ];
  
  async function handleExport(format: string) {
    if (!data && !charts && !rosbagData) return;
    setExporting(format);
    setProgress(0);
    
    try {
      switch (format) {
        case 'pdf':
          if (charts) {
            await exportChartsAsPDF(charts, { filename, title, orientation: 'landscape' });
          }
          break;
        case 'png':
          if (charts) {
            for (let i = 0; i < charts.length; i++) {
              const chart = charts[i];
              await exportChartAsPNG(chart.element, { filename: `${filename}_${chart.title.replace(/\s+/g, '_')}` });
              setProgress((i + 1) / charts.length);
            }
          }
          break;
        case 'svg':
          if (charts) {
            for (const chart of charts) {
              await exportChartAsSVG(chart.element, { filename: `${filename}_${chart.title.replace(/\s+/g, '_')}` });
            }
          }
          break;
        case 'csv':
          if (data) exportAsCSV(data, filename);
          break;
        case 'json':
          if (data) exportAsJSON({ data, metadata, exported_at: Date.now() }, filename);
          break;
        case 'xlsx':
          if (data) {
            if (metadata?.sheets) {
              exportMultiSheetExcel(metadata.sheets, filename);
            } else {
              exportAsExcel(data, filename);
            }
          }
          break;
        case 'rosbag':
          if (rosbagData) {
            await exportAsRosbag(rosbagData);
          }
          break;
        case 'jsonl':
          if (rosbagData?.messages) {
            exportAsJsonl(rosbagData.messages, filename);
          }
          break;
      }
      setProgress(1);
      setTimeout(() => {
        setExporting(null);
        onClose();
      }, 500);
    } catch (er) {
      console.error('Export failed:', er);
      setExporting(null);
    }
  }
  
  return (
    <Modal open={open} onClose={onClose} title="Export Data & Reports">
      <div className="grid grid-cols-2 gap-3">
        {exportFormats.map((format) => {
          const Icon = format.icon;
          const isExporting = exporting === format.id;
          return (
            <button
              key={format.id}
              onClick={() => handleExport(format.id)}
              disabled={!!exporting && !isExporting}
              className={cn(
                'p-4 bg-surface border border-border rounded-theme-md text-left transition-all',
                'hover:border-primary-500 hover:bg-surface-hover',
                isExporting && 'border-primary-500 bg-primary-500/10'
              )}
            >
              <div className="flex items-center gap-3">
                <Icon className="w-6 h-6 text-primary-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-text text-sm">{format.label}</div>
                  <div className="text-xs text-text-tertiary truncate">{format.description}</div>
                </div>
              </div>
              {isExporting && (
                <div className="mt-2 h-1 bg-surface-elevated rounded-full overflow-hidden">
                  <div className="h-full bg-primary-500 transition-all" style={{ width: `${progress * 100}%` }} />
                </div>
              )}
            </button>
          );
        })}
      </div>
    </Modal>
  );
}
