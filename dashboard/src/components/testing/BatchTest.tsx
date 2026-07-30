import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Play, Loader2, GitCompare, FileSpreadsheet } from 'lucide-react';
import { testingApi } from '@/testing/api';
import { ConfusionMatrixHeatmap } from '@/components/ml/ConfusionMatrixHeatmap';
import { useTheme } from '@/themes/ThemeProvider';
import { toast } from 'sonner';

export function BatchTest() {
  const { theme } = useTheme();
  
  const [testRunId, setTestRunId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('1.5.0');
  const [comparisonModelId, setComparisonModelId] = useState<string>('1.4.0');
  const [datasetId, setDatasetId] = useState<string>('ds1');
  const [isABTest, setIsABTest] = useState(false);
  const [config, setConfig] = useState({
    confidenceThreshold: 0.5,
    iouThreshold: 0.45,
  });
  
  const { data: testRun } = useQuery({
    queryKey: ['test-run', testRunId],
    queryFn: () => testingApi.getTestRun(testRunId!),
    enabled: !!testRunId,
    refetchInterval: (query) => {
      const data = query.state.data;
      return data?.status === 'processing' ? 2000 : false;
    },
  });
  
  const handleStart = async () => {
    try {
      if (isABTest) {
        const result = await testingApi.createABTest(selectedModel, comparisonModelId, datasetId);
        setTestRunId(result.test_run_id);
        toast.success('A/B Test initiated');
      } else {
        const result = await testingApi.createTestRun({
          name: `Batch test ${new Date().toLocaleTimeString()}`,
          modelId: selectedModel,
          testType: 'batch',
          datasetId,
          config,
          comparisonModelId: comparisonModelId || undefined,
        });
        setTestRunId(result.id);
        toast.success('Batch test run created');
      }
    } catch (err: any) {
      toast.error(`Failed to start: ${err.message}`);
    }
  };
  
  const mockMetrics = testRun?.metrics || {
    mAP50: 0.892,
    precision: 0.865,
    recall: 0.834,
    avgInferenceMs: 18.5,
  };
  
  const mockConfusion = testRun?.confusionMatrix || {
    classes: ['co2_emitter', 'capture_unit', 'equipment', 'pipeline', 'valve', 'tank'],
    matrix: [
      [850, 20, 15, 10, 3, 2],
      [18, 890, 12, 5, 2, 3],
      [12, 15, 870, 20, 5, 8],
      [8, 10, 15, 910, 10, 2],
      [5, 4, 8, 12, 860, 15],
      [3, 5, 10, 5, 12, 880],
    ],
  };
  
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-text">Batch & A/B Model Testing</h1>
        <p className="text-text-secondary text-sm">Execute large dataset validation, cross-model comparison, and regression testing</p>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-3 bg-surface border border-border rounded-theme-md p-4 space-y-3">
          <h3 className="font-semibold text-text">Batch Test Settings</h3>
          
          <div className="flex gap-2">
            <button
              onClick={() => setIsABTest(false)}
              className={`flex-1 py-1 text-xs rounded border ${!isABTest ? 'bg-primary-500 text-white font-medium border-primary-500' : 'bg-surface-elevated text-text-secondary border-border'}`}
            >
              Batch Run
            </button>
            <button
              onClick={() => setIsABTest(true)}
              className={`flex-1 py-1 text-xs rounded border ${isABTest ? 'bg-primary-500 text-white font-medium border-primary-500' : 'bg-surface-elevated text-text-secondary border-border'}`}
            >
              A/B Compare
            </button>
          </div>
          
          <div>
            <label className="text-xs text-text-tertiary uppercase">Model A (Primary)</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text mt-1 text-xs"
            >
              <option value="1.5.0">YOLOv8-Carbonize v1.5.0</option>
              <option value="1.4.0">YOLOv8-Carbonize v1.4.0</option>
            </select>
          </div>
          
          {isABTest && (
            <div>
              <label className="text-xs text-text-tertiary uppercase">Model B (Challenger)</label>
              <select
                value={comparisonModelId}
                onChange={(e) => setComparisonModelId(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text mt-1 text-xs"
              >
                <option value="1.4.0">YOLOv8-Carbonize v1.4.0</option>
                <option value="1.3.0">YOLOv5-Nano v1.3.0</option>
              </select>
            </div>
          )}
          
          <div>
            <label className="text-xs text-text-tertiary uppercase">Dataset</label>
            <select
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
              className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text mt-1 text-xs"
            >
              <option value="ds1">Validation Benchmark (5,000 images)</option>
              <option value="ds2">Edge Hardware Stress Set (1,000 images)</option>
              <option value="ds3">Low Light & Weather Set (2,500 images)</option>
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
          
          <button onClick={handleStart} className="theme-button-primary w-full text-xs font-semibold">
            {isABTest ? <GitCompare className="w-4 h-4 inline mr-2" /> : <Play className="w-4 h-4 inline mr-2" />}
            {isABTest ? 'Run A/B Comparison' : 'Start Batch Test'}
          </button>
        </div>
        
        <div className="col-span-9 space-y-4">
          <div className="grid grid-cols-4 gap-3">
            <MetricCard label="mAP50" value={`${(mockMetrics.mAP50 * 100).toFixed(1)}%`} />
            <MetricCard label="Precision" value={`${(mockMetrics.precision * 100).toFixed(1)}%`} />
            <MetricCard label="Recall" value={`${(mockMetrics.recall * 100).toFixed(1)}%`} />
            <MetricCard label="Avg Latency" value={`${mockMetrics.avgInferenceMs.toFixed(1)}ms`} />
          </div>
          
          <ConfusionMatrixHeatmap
            classes={mockConfusion.classes}
            matrix={mockConfusion.matrix}
            normalized={mockConfusion.matrix.map((row: number[]) => {
              const sum = row.reduce((a: number, b: number) => a + b, 0);
              return row.map((v: number) => v / sum);
            })}
          />
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface border border-border rounded-theme-md p-3">
      <div className="text-xs text-text-tertiary">{label}</div>
      <div className="text-2xl font-bold text-text font-mono mt-1">{value}</div>
    </div>
  );
}
