import { toPng, toSvg } from 'html-to-image';
import jsPDF from 'jspdf';
import { saveAs } from 'file-saver';

export interface ChartExportOptions {
  filename: string;
  pixelRatio?: number;
  backgroundColor?: string;
  width?: number;
  height?: number;
  filter?: (node: HTMLElement) => boolean;
}

export async function exportChartAsPNG(element: HTMLElement, options: ChartExportOptions): Promise<Blob> {
  const dataUrl = await toPng(element, {
    pixelRatio: options.pixelRatio || 3,
    backgroundColor: options.backgroundColor || '#0f172a',
    cacheBust: true,
    filter: options.filter,
  });
  
  const blob = await fetch(dataUrl).then((r) => r.blob());
  saveAs(blob, `${options.filename}.png`);
  return blob;
}

export async function exportChartAsSVG(element: HTMLElement, options: ChartExportOptions): Promise<Blob> {
  const dataUrl = await toSvg(element, {
    backgroundColor: options.backgroundColor || '#0f172a',
    filter: options.filter,
  });
  
  const blob = await fetch(dataUrl).then((r) => r.blob());
  saveAs(blob, `${options.filename}.svg`);
  return blob;
}

export async function exportChartsAsPDF(
  charts: Array<{ title: string; element: HTMLElement }>,
  options: { filename: string; title?: string; orientation?: 'portrait' | 'landscape' }
): Promise<Blob> {
  const pdf = new jsPDF({
    orientation: options.orientation || 'landscape',
    unit: 'mm',
    format: 'a4',
  });
  
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const contentWidth = pageWidth - 2 * margin;
  
  if (options.title) {
    pdf.setFontSize(20);
    pdf.text(options.title, pageWidth / 2, 30, { align: 'center' });
    
    pdf.setFontSize(10);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, pageWidth / 2, 40, { align: 'center' });
  }
  
  for (let i = 0; i < charts.length; i++) {
    if (i > 0 || options.title) pdf.addPage();
    const { title, element } = charts[i];
    
    pdf.setFontSize(14);
    pdf.text(title, margin, margin + 5);
    
    const dataUrl = await toPng(element, { pixelRatio: 2, backgroundColor: '#0f172a' });
    const img = await loadImage(dataUrl);
    const ratio = img.width / img.height;
    const chartHeight = contentWidth / ratio;
    
    pdf.addImage(dataUrl, 'PNG', margin, margin + 12, contentWidth, Math.min(chartHeight, pageHeight - 40));
  }
  
  const blob = pdf.output('blob');
  saveAs(blob, `${options.filename}.pdf`);
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
