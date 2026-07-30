import { useState, useRef } from 'react';
import { Upload, Play, Loader2, Image as ImageIcon } from 'lucide-react';
import { ImageAnnotator } from './ImageAnnotator';
import { testingApi } from '@/testing/api';
import type { BoundingBox } from '@/ml/types';
import type { TestConfig } from '@/testing/types';
import { useTheme } from '@/themes/ThemeProvider';
import { toast } from 'sonner';

export function SingleImageTest() {
  const { theme } = useTheme();
  
  const [selectedModel, setSelectedModel] = useState<string>('1.5.0');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [imageDims, setImageDims] = useState({ width: 640, height: 480 });
  const [predictions, setPredictions] = useState<BoundingBox[]>([]);
  const [groundTruth, setGroundTruth] = useState<BoundingBox[]>([]);
  const [loading, setLoading] = useState(false);
  const [inferenceTime, setInferenceTime] = useState(0);
  const [config, setConfig] = useState<TestConfig>({
    modelId: selectedModel,
    confidenceThreshold: 0.5,
    iouThreshold: 0.45,
    maxDetections: 100,
    returnAnnotatedImage: true,
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setImageFile(file);
    const url = URL.createObjectURL(file);
    setImageUrl(url);
    
    const img = new Image();
    img.onload = () => {
      setImageDims({ width: img.width, height: img.height });
    };
    img.src = url;
    
    setPredictions([]);
    setGroundTruth([]);
  };
  
  const handlePredict = async () => {
    if (!imageUrl) {
      toast.error('Please upload an image first');
      return;
    }
    
    setLoading(true);
    try {
      if (imageFile) {
        const result = await testingApi.predictSingle(selectedModel, imageFile, {
          ...config,
          modelId: selectedModel,
        });
        setPredictions(result.detections || []);
        setInferenceTime(result.inference_time_ms || 18.5);
        toast.success(`Found ${(result.detections || []).length} detections`);
      } else {
        // Fallback demo predictions
        setPredictions([
          { x_min: 50, y_min: 50, x_max: 200, y_max: 200, confidence: 0.92, class_id: 0, class_name: 'co2_emitter' },
          { x_min: 250, y_min: 100, x_max: 400, y_max: 300, confidence: 0.85, class_id: 1, class_name: 'capture_unit' },
        ]);
        setInferenceTime(18.5);
        toast.success('Inference complete (demo mode)');
      }
    } catch (err: any) {
      toast.error(`Inference failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-text">Single Image Test Sandbox</h1>
        <p className="text-text-secondary text-sm">Upload images, annotate bounding boxes, and test edge device hardware profiles</p>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-3 bg-surface border border-border rounded-theme-md p-4 space-y-4">
          <h3 className="font-semibold text-text">Test Configuration</h3>
          
          <div>
            <label className="text-xs text-text-tertiary uppercase">Model</label>
            <select
              value={selectedModel}
              onChange={(e) => { setSelectedModel(e.target.value); setConfig({ ...config, modelId: e.target.value }); }}
              className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text mt-1 text-sm"
            >
              <option value="1.5.0">YOLOv8-Carbonize v1.5.0 (Prod)</option>
              <option value="1.4.0">YOLOv8-Carbonize v1.4.0</option>
              <option value="1.3.0">YOLOv5-Nano v1.3.0</option>
            </select>
          </div>
          
          <div>
            <label className="text-xs text-text-tertiary uppercase flex justify-between">
              <span>Confidence</span>
              <span className="text-text font-mono">{(config.confidenceThreshold * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range" min="0" max="1" step="0.05"
              value={config.confidenceThreshold}
              onChange={(e) => setConfig({ ...config, confidenceThreshold: parseFloat(e.target.value) })}
              className="w-full accent-primary-500 mt-1"
            />
          </div>
          
          <div>
            <label className="text-xs text-text-tertiary uppercase flex justify-between">
              <span>IoU Threshold</span>
              <span className="text-text font-mono">{config.iouThreshold.toFixed(2)}</span>
            </label>
            <input
              type="range" min="0" max="1" step="0.05"
              value={config.iouThreshold}
              onChange={(e) => setConfig({ ...config, iouThreshold: parseFloat(e.target.value) })}
              className="w-full accent-primary-500 mt-1"
            />
          </div>
          
          <div>
            <label className="flex items-center gap-2 text-xs text-text-secondary">
              <input
                type="checkbox"
                checked={config.edgeSimulator?.enabled || false}
                onChange={(e) => setConfig({
                  ...config,
                  edgeSimulator: e.target.checked
                    ? { enabled: true, device: 'jetson_nano' }
                    : undefined,
                })}
                className="accent-primary-500"
              />
              Edge Device Simulator
            </label>
            {config.edgeSimulator?.enabled && (
              <select
                value={config.edgeSimulator.device}
                onChange={(e) => setConfig({
                  ...config,
                  edgeSimulator: { ...config.edgeSimulator!, device: e.target.value as any },
                })}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-1 text-text mt-1 text-xs"
              >
                <option value="jetson_nano">Jetson Nano (15W, 50ms)</option>
                <option value="jetson_xavier">Jetson Xavier (30W, 25ms)</option>
                <option value="cpu_only">CPU Server (65W, 200ms)</option>
                <option value="raspberry_pi">Raspberry Pi 4 (5W, 500ms)</option>
              </select>
            )}
          </div>
          
          {predictions.length > 0 && (
            <div className="bg-surface-elevated rounded-theme-md p-3 text-xs space-y-1">
              <div className="flex justify-between"><span className="text-text-tertiary">Detections:</span><span className="text-text font-mono">{predictions.length}</span></div>
              <div className="flex justify-between"><span className="text-text-tertiary">Inference:</span><span className="text-text font-mono">{inferenceTime.toFixed(1)}ms</span></div>
              <div className="flex justify-between"><span className="text-text-tertiary">Avg conf:</span><span className="text-text font-mono">{(predictions.reduce((a, b) => a + b.confidence, 0) / predictions.length * 100).toFixed(1)}%</span></div>
            </div>
          )}
        </div>
        
        <div className="col-span-9 space-y-3">
          {!imageUrl ? (
            <div
              className="bg-surface border-2 border-dashed border-border rounded-theme-md p-12 text-center cursor-pointer hover:border-primary-500"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-12 h-12 mx-auto text-text-tertiary mb-3" />
              <p className="text-text-secondary">Drop image here or click to upload</p>
              <p className="text-xs text-text-tertiary mt-1">PNG, JPG, WebP supported</p>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2">
                <button onClick={() => fileInputRef.current?.click()} className="theme-button text-xs">
                  <ImageIcon className="w-4 h-4 inline mr-1" />
                  Change Image
                </button>
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                <button onClick={handlePredict} disabled={loading} className="theme-button-primary text-xs font-semibold">
                  {loading ? <Loader2 className="w-4 h-4 inline mr-1 animate-spin" /> : <Play className="w-4 h-4 inline mr-1" />}
                  Run Inference
                </button>
              </div>
              <ImageAnnotator
                imageUrl={imageUrl}
                imageWidth={imageDims.width}
                imageHeight={imageDims.height}
                annotations={groundTruth}
                predictions={predictions}
                groundTruth={groundTruth}
                classes={['co2_emitter', 'capture_unit', 'equipment', 'pipeline']}
                onAnnotationsChange={setGroundTruth}
                showPredictions={true}
                showGroundTruth={true}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
