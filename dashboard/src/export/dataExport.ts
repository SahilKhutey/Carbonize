import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';

export function exportAsCSV(data: any[], filename: string): Blob {
  const csv = Papa.unparse(data);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  saveAs(blob, `${filename}.csv`);
  return blob;
}

export function exportAsJSON(data: any, filename: string, pretty = true): Blob {
  const json = pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);
  const blob = new Blob([json], { type: 'application/json' });
  saveAs(blob, `${filename}.json`);
  return blob;
}

export function exportAsExcel(data: any[], filename: string, sheetName = 'Data'): Blob {
  const worksheet = XLSX.utils.json_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
  
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(blob, `${filename}.xlsx`);
  return blob;
}

export function exportMultiSheetExcel(
  datasets: Array<{ name: string; data: any[] }>,
  filename: string
): Blob {
  const workbook = XLSX.utils.book_new();
  datasets.forEach(({ name, data }) => {
    const ws = XLSX.utils.json_to_sheet(data);
    XLSX.utils.book_append_sheet(workbook, ws, name.slice(0, 31));
  });
  
  const buffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(blob, `${filename}.xlsx`);
  return blob;
}

export async function exportAsParquet(data: any[], filename: string): Promise<Blob> {
  const response = await fetch('/api/v1/export/parquet', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data }),
  });
  
  if (!response.ok) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    saveAs(blob, `${filename}.json`);
    return blob;
  }
  
  const blob = await response.blob();
  saveAs(blob, `${filename}.parquet`);
  return blob;
}
