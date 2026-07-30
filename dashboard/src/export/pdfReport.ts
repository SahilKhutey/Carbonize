import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { toPng } from 'html-to-image';
import { saveAs } from 'file-saver';
import type { ModelPerformanceMetrics, ConfusionMatrix } from '@/ml/types';

interface ReportSection {
  title: string;
  type: 'text' | 'table' | 'chart' | 'image';
  content?: any;
  element?: HTMLElement;
}

interface ReportConfig {
  title: string;
  subtitle?: string;
  author?: string;
  company?: string;
  sections: ReportSection[];
  includeTimestamp?: boolean;
  watermark?: string;
}

export async function generatePDFReport(config: ReportConfig): Promise<Blob> {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 15;
  const contentWidth = pageWidth - 2 * margin;
  
  let yPos = margin;
  
  pdf.setFillColor(34, 197, 94);
  pdf.rect(0, 0, pageWidth, 40, 'F');
  
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(24);
  pdf.setFont('helvetica', 'bold');
  pdf.text(config.title, margin, 25);
  
  if (config.subtitle) {
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    pdf.text(config.subtitle, margin, 33);
  }
  
  pdf.setTextColor(0, 0, 0);
  yPos = 60;
  
  pdf.setFontSize(10);
  pdf.text(`Generated: ${new Date().toLocaleString()}`, margin, yPos);
  yPos += 5;
  if (config.author) {
    pdf.text(`Author: ${config.author}`, margin, yPos);
    yPos += 5;
  }
  if (config.company) {
    pdf.text(`Company: ${config.company}`, margin, yPos);
    yPos += 10;
  }
  
  if (config.watermark) {
    pdf.setTextColor(200, 200, 200);
    pdf.setFontSize(60);
    pdf.text(config.watermark, pageWidth / 2, pageHeight / 2, {
      align: 'center',
      angle: 45,
    });
    pdf.setTextColor(0, 0, 0);
  }
  
  for (const section of config.sections) {
    if (yPos > pageHeight - 30) {
      pdf.addPage();
      yPos = margin;
    }
    
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text(section.title, margin, yPos);
    yPos += 8;
    
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(10);
    
    if (section.type === 'text') {
      const lines = pdf.splitTextToSize(section.content, contentWidth);
      pdf.text(lines, margin, yPos);
      yPos += lines.length * 5 + 5;
    }
    else if (section.type === 'table') {
      autoTable(pdf, {
        startY: yPos,
        head: [section.content.headers],
        body: section.content.rows,
        margin: { left: margin, right: margin },
        styles: { fontSize: 9 },
        headStyles: { fillColor: [34, 197, 94] },
      });
      // @ts-ignore
      yPos = pdf.lastAutoTable.finalY + 10;
    }
    else if (section.type === 'chart' && section.element) {
      const dataUrl = await toPng(section.element, { pixelRatio: 2, backgroundColor: '#ffffff' });
      const img = await loadImage(dataUrl);
      const ratio = img.width / img.height;
      const chartHeight = contentWidth / ratio;
      
      if (yPos + chartHeight > pageHeight - margin) {
        pdf.addPage();
        yPos = margin;
      }
      
      pdf.addImage(dataUrl, 'PNG', margin, yPos, contentWidth, chartHeight);
      yPos += chartHeight + 10;
    }
  }
  
  const pageCount = pdf.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(8);
    pdf.setTextColor(128, 128, 128);
    pdf.text(`Page ${i} of ${pageCount}`, pageWidth - margin, pageHeight - 5, { align: 'right' });
    pdf.text('Carbonize ML Analytics Report', margin, pageHeight - 5);
  }
  
  const blob = pdf.output('blob');
  saveAs(blob, `${config.title.replace(/\s+/g, '_')}_${Date.now()}.pdf`);
  return blob;
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

export async function generateModelPerformanceReport(
  metrics: ModelPerformanceMetrics,
  charts: Array<{ title: string; element: HTMLElement }>,
  perClassMetrics: any[],
  _confusionMatrix: ConfusionMatrix
): Promise<Blob> {
  return generatePDFReport({
    title: 'Model Performance Report',
    subtitle: `Version ${metrics.modelVersion}`,
    company: 'Carbonize',
    sections: [
      {
        title: 'Overview',
        type: 'text',
        content: `This report provides a comprehensive analysis of the model's performance metrics as of ${new Date(metrics.timestamp).toLocaleString()}.`,
      },
      {
        title: 'Key Metrics',
        type: 'table',
        content: {
          headers: ['Metric', 'Value'],
          rows: [
            ['mAP@50', `${(metrics.mAP50 * 100).toFixed(2)}%`],
            ['mAP@50-95', `${(metrics.mAP50_95 * 100).toFixed(2)}%`],
            ['Precision', `${(metrics.precision * 100).toFixed(2)}%`],
            ['Recall', `${(metrics.recall * 100).toFixed(2)}%`],
            ['F1 Score', `${(metrics.f1Score * 100).toFixed(2)}%`],
            ['Accuracy', `${(metrics.accuracy * 100).toFixed(2)}%`],
            ['Inference Latency', `${metrics.inferenceLatencyMs.toFixed(2)} ms`],
            ['Throughput', `${metrics.throughputFps.toFixed(1)} FPS`],
            ['GPU Utilization', `${metrics.gpuUtilization.toFixed(0)}%`],
          ],
        },
      },
      ...charts.map((chart) => ({
        title: chart.title,
        type: 'chart' as const,
        element: chart.element,
      })),
      {
        title: 'Per-Class Performance',
        type: 'table',
        content: {
          headers: ['Class', 'Precision', 'Recall', 'F1', 'Support'],
          rows: perClassMetrics.map((m) => [
            m.className,
            `${(m.precision * 100).toFixed(1)}%`,
            `${(m.recall * 100).toFixed(1)}%`,
            `${(m.f1Score * 100).toFixed(1)}%`,
            m.support.toString(),
          ]),
        },
      },
    ],
  });
}
