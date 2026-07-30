import { useRef, useState, useEffect, useCallback } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Trash2, Crosshair } from 'lucide-react';
import type { BoundingBox } from '@/ml/types';

interface ImageAnnotatorProps {
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
  annotations: BoundingBox[];
  predictions?: BoundingBox[];
  groundTruth?: BoundingBox[];
  selectedClass?: string;
  classes?: string[];
  readOnly?: boolean;
  onAnnotationsChange?: (annotations: BoundingBox[]) => void;
  showPredictions?: boolean;
  showGroundTruth?: boolean;
}

interface DrawingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export function ImageAnnotator({
  imageUrl,
  imageWidth,
  imageHeight,
  annotations,
  predictions,
  groundTruth,
  selectedClass = '0',
  classes = [],
  readOnly = false,
  onAnnotationsChange,
  showPredictions = true,
  showGroundTruth = true,
}: ImageAnnotatorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingBox, setDrawingBox] = useState<DrawingBox | null>(null);
  const [hoveredBox, setHoveredBox] = useState<number | null>(null);
  const [selectedBox, setSelectedBox] = useState<number | null>(null);

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const dpr = window.devicePixelRatio || 1;
    const w = imageWidth || img.width || 640;
    const h = imageHeight || img.height || 480;
    
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w * zoom}px`;
    canvas.style.height = `${h * zoom}px`;
    ctx.scale(dpr, dpr);
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, w, h);
    
    if (showGroundTruth && groundTruth) {
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      groundTruth.forEach((box) => {
        ctx.strokeRect(box.x_min, box.y_min, box.x_max - box.x_min, box.y_max - box.y_min);
      });
      ctx.setLineDash([]);
    }
    
    if (showPredictions && predictions) {
      predictions.forEach((box, i) => {
        const isSelected = selectedBox === i;
        ctx.strokeStyle = isSelected ? '#fbbf24' : '#3b82f6';
        ctx.lineWidth = isSelected ? 3 : 2;
        ctx.strokeRect(box.x_min, box.y_min, box.x_max - box.x_min, box.y_max - box.y_min);
        
        const label = `${classes[box.class_id] || box.class_name || `cls_${box.class_id}`} ${(box.confidence * 100).toFixed(0)}%`;
        ctx.font = '12px sans-serif';
        const labelWidth = ctx.measureText(label).width + 8;
        ctx.fillStyle = isSelected ? '#fbbf24' : '#3b82f6';
        ctx.fillRect(box.x_min, Math.max(0, box.y_min - 18), labelWidth, 18);
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, box.x_min + 4, Math.max(12, box.y_min - 5));
      });
    }
    
    annotations.forEach((box, i) => {
      const isSelected = selectedBox === i;
      ctx.strokeStyle = isSelected ? '#fbbf24' : '#eab308';
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.strokeRect(box.x_min, box.y_min, box.x_max - box.x_min, box.y_max - box.y_min);
    });
    
    if (drawingBox) {
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(
        drawingBox.x_min,
        drawingBox.y_min,
        drawingBox.x_max - drawingBox.x_min,
        drawingBox.y_max - drawingBox.y_min,
      );
      ctx.setLineDash([]);
    }
  }, [imageWidth, imageHeight, annotations, predictions, groundTruth, drawingBox, zoom, selectedBox, hoveredBox, showPredictions, showGroundTruth, classes]);

  useEffect(() => {
    if (!imageUrl) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      imageRef.current = img;
      drawCanvas();
    };
    img.src = imageUrl;
  }, [imageUrl, drawCanvas]);
  
  useEffect(() => {
    drawCanvas();
  }, [drawCanvas]);
  
  const getCanvasCoords = (e: React.MouseEvent): { x: number; y: number } => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom;
    const y = (e.clientY - rect.top) / zoom;
    return { x, y };
  };
  
  const handleMouseDown = (e: React.MouseEvent) => {
    if (readOnly) return;
    const { x, y } = getCanvasCoords(e);
    setIsDrawing(true);
    setDrawingBox({ x_min: x, y_min: y, x_max: x, y_max: y });
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    const { x, y } = getCanvasCoords(e);
    if (isDrawing) {
      setDrawingBox((prev) => prev ? { ...prev, x_max: x, y_max: y } : null);
    }
  };
  
  const handleMouseUp = () => {
    if (isDrawing && drawingBox) {
      const newBox: BoundingBox = {
        x_min: Math.min(drawingBox.x_min, drawingBox.x_max),
        y_min: Math.min(drawingBox.y_min, drawingBox.y_max),
        x_max: Math.max(drawingBox.x_min, drawingBox.x_max),
        y_max: Math.max(drawingBox.y_min, drawingBox.y_max),
        confidence: 1.0,
        class_id: parseInt(selectedClass) || 0,
        class_name: classes[parseInt(selectedClass)] || `class_${selectedClass}`,
      };
      if (newBox.x_max - newBox.x_min > 5 && newBox.y_max - newBox.y_min > 5) {
        onAnnotationsChange?.([...annotations, newBox]);
      }
    }
    setIsDrawing(false);
    setDrawingBox(null);
  };
  
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2 bg-surface border border-border rounded-theme-md p-2">
        <button onClick={() => setZoom((z) => Math.min(4, z * 1.2))} className="theme-button p-1">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button onClick={() => setZoom((z) => Math.max(0.25, z / 1.2))} className="theme-button p-1">
          <ZoomOut className="w-4 h-4" />
        </button>
        <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }} className="theme-button p-1">
          <RotateCcw className="w-4 h-4" />
        </button>
        <span className="text-xs text-text-tertiary font-mono">{(zoom * 100).toFixed(0)}%</span>
        
        {!readOnly && (
          <>
            <div className="flex-1" />
            <button onClick={() => { onAnnotationsChange?.([]); setSelectedBox(null); }} className="theme-button p-1">
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        )}
      </div>
      
      <div ref={containerRef} className="bg-surface-elevated border border-border rounded-theme-md overflow-hidden flex items-center justify-center p-2">
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={() => { setIsDrawing(false); setDrawingBox(null); }}
          style={{
            display: 'block',
            cursor: readOnly ? 'default' : 'crosshair',
          }}
        />
      </div>
    </div>
  );
}
