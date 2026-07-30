import { useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { mlAnalyticsApi } from '@/ml/api';
import { DriftMonitor } from '@/components/ml/DriftMonitor';
import { ConfusionMatrixHeatmap } from '@/components/ml/ConfusionMatrixHeatmap';
import { PerClassMetrics } from '@/components/ml/PerClassMetrics';
import { ROCCurveChart } from '@/components/ml/ROCCurveChart';
import { CalibrationPlot } from '@/components/ml/CalibrationPlot';
import { AblationStudy } from '@/components/ml/AblationStudy';
import { FairnessAnalysis } from '@/components/ml/FairnessAnalysis';
import { PerformanceMonitor } from '@/components/ml/PerformanceMonitor';
import { ExportButton } from '@/components/export/ExportButton';
import { ScheduledReports } from '@/components/export/ScheduledReports';
import { generatePerClassMetrics, generateAblationResults, generateFairnessMetrics, generateROCCurve } from '@/ml/mockData';
import { Brain, Layers, GitCompare, Zap, Mail } from 'lucide-react';
import { cn } from '@/lib/utils';

const TABS = [
  { id: 'performance', label: 'Performance', icon: Zap },
  { id: 'drift', label: 'Drift', icon: GitCompare },
  { id: 'classes', label: 'Per-Class', icon: Layers },
  { id: 'curves', label: 'ROC/PR', icon: Brain },
  { id: 'ablation', label: 'Ablation', icon: Brain },
  { id: 'fairness', label: 'Fairness', icon: Brain },
];

export function MLAnalytics() {
  const [activeTab, setActiveTab] = useState('performance');
  const [modelVersion, setModelVersion] = useState('1.5.0');
  const [scheduledOpen, setScheduledOpen] = useState(false);
  
  const contentRef = useRef<HTMLDivElement>(null);
  
  const { data: perClass = [] } = useQuery({
    queryKey: ['per-class', modelVersion],
    queryFn: () => mlAnalyticsApi.getPerClassMetrics(modelVersion),
  });
  
  const { data: confusionMatrix } = useQuery({
    queryKey: ['confusion', modelVersion],
    queryFn: () => mlAnalyticsApi.getConfusionMatrix(modelVersion),
  });
  
  const { data: calibration } = useQuery({
    queryKey: ['calibration', modelVersion],
    queryFn: () => mlAnalyticsApi.getCalibration(modelVersion),
  });
  
  const { data: ablation = [] } = useQuery({
    queryKey: ['ablation', 'main'],
    queryFn: () => mlAnalyticsApi.getAblationResults('main'),
  });
  
  const { data: fairness } = useQuery({
    queryKey: ['fairness', modelVersion],
    queryFn: () => mlAnalyticsApi.getFairnessMetrics(modelVersion, 'lighting'),
  });
  
  const rocCurves = (perClass.length > 0 ? perClass.map((c) => ({
    className: c.className,
    data: generateROCCurve(),
  })) : generatePerClassMetrics().map((c) => ({
    className: c.className,
    data: generateROCCurve(),
  })));
  
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Brain className="w-7 h-7 text-primary-500" />
            ML Analytics & Export System
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            Performance monitoring, drift detection, calibration, and complete report generation
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={modelVersion}
            onChange={(e) => setModelVersion(e.target.value)}
            className="bg-surface border border-border rounded-theme-md px-3 py-2 text-text text-sm"
          >
            <option value="1.5.0">v1.5.0 (Production)</option>
            <option value="1.4.0">v1.4.0</option>
            <option value="1.3.0">v1.3.0</option>
          </select>
          <button
            onClick={() => setScheduledOpen(true)}
            className="theme-button flex items-center gap-2 text-sm"
          >
            <Mail className="w-4 h-4" />
            Schedule
          </button>
          <ExportButton
            data={perClass.length > 0 ? perClass : generatePerClassMetrics()}
            filename={`ml_analytics_${modelVersion}`}
            title={`ML Analytics Report - ${modelVersion}`}
            metadata={{ modelVersion, exportedAt: Date.now() }}
            label="Export Data / Report"
          />
        </div>
      </div>
      
      <div className="flex gap-1 bg-surface border border-border rounded-theme-md p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-theme-md text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-primary-500 text-white shadow-theme-sm'
                : 'text-text-secondary hover:bg-surface-hover hover:text-text'
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>
      
      <div ref={contentRef} className="animate-fade-in">
        {activeTab === 'performance' && <PerformanceMonitor />}
        {activeTab === 'drift' && <DriftMonitor />}
        {activeTab === 'classes' && (
          <div className="space-y-4">
            <PerClassMetrics metrics={perClass.length > 0 ? perClass : generatePerClassMetrics()} />
            {confusionMatrix && <ConfusionMatrixHeatmap {...confusionMatrix} />}
          </div>
        )}
        {activeTab === 'curves' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ROCCurveChart curves={rocCurves} type="roc" />
            <ROCCurveChart curves={rocCurves} type="pr" />
            {calibration && <CalibrationPlot data={calibration} />}
          </div>
        )}
        {activeTab === 'ablation' && (
          <AblationStudy results={ablation.length > 0 ? ablation : generateAblationResults()} />
        )}
        {activeTab === 'fairness' && (
          <FairnessAnalysis metrics={fairness || generateFairnessMetrics()} />
        )}
      </div>
      
      <ScheduledReports open={scheduledOpen} onClose={() => setScheduledOpen(false)} />
    </div>
  );
}
