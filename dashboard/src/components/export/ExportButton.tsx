import { Download } from 'lucide-react';
import { useExport } from '@/hooks/useExport';

interface ExportButtonProps {
  data?: any[];
  charts?: Array<{ title: string; element: HTMLElement }>;
  rosbagData?: any;
  filename?: string;
  title?: string;
  metadata?: Record<string, any>;
  variant?: 'primary' | 'secondary';
  label?: string;
}

export function ExportButton({ data, charts, rosbagData, filename, title, metadata, variant = 'primary', label = 'Export' }: ExportButtonProps) {
  const { openExport } = useExport();
  
  return (
    <button
      onClick={() => openExport({ data, charts, rosbagData, filename, title, metadata })}
      className={variant === 'primary' ? 'theme-button-primary flex items-center gap-2 text-sm font-semibold' : 'theme-button flex items-center gap-2 text-sm'}
    >
      <Download className="w-4 h-4" />
      {label}
    </button>
  );
}
