import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { Layout } from '@/components/Layout';
import { ThemeProvider } from '@/themes/ThemeProvider';
import { ExportProvider, useExport } from '@/hooks/useExport';
import { ExportDialog } from '@/components/export/ExportDialog';

const TelemetryOverview = lazy(() => import('@/pages/TelemetryOverview').then((m) => ({ default: m.TelemetryOverview })));
const Scene3D = lazy(() => import('@/pages/Scene3D').then((m) => ({ default: m.Scene3D })));
const Simulation = lazy(() => import('@/pages/Simulation').then((m) => ({ default: m.Simulation })));
const Detections = lazy(() => import('@/pages/Detections').then((m) => ({ default: m.Detections })));
const Models = lazy(() => import('@/pages/Models').then((m) => ({ default: m.Models })));
const Analytics = lazy(() => import('@/pages/Analytics').then((m) => ({ default: m.Analytics })));
const AdvancedAnalytics = lazy(() => import('@/pages/AdvancedAnalytics').then((m) => ({ default: m.AdvancedAnalytics })));
const MLAnalytics = lazy(() => import('@/pages/MLAnalytics').then((m) => ({ default: m.MLAnalytics })));
const SingleImageTest = lazy(() => import('@/components/testing/SingleImageTest').then((m) => ({ default: m.SingleImageTest })));
const BatchTest = lazy(() => import('@/components/testing/BatchTest').then((m) => ({ default: m.BatchTest })));
const PredictiveAnalytics = lazy(() => import('@/pages/PredictiveAnalytics').then((m) => ({ default: m.PredictiveAnalytics })));
const StreamingDashboard = lazy(() => import('@/pages/StreamingDashboard').then((m) => ({ default: m.StreamingDashboard })));
const DriftDashboard = lazy(() => import('@/pages/DriftDashboard').then((m) => ({ default: m.DriftDashboard })));
const AnomalyInvestigation = lazy(() => import('@/pages/AnomalyInvestigation').then((m) => ({ default: m.AnomalyInvestigation })));
const GameDayDashboard = lazy(() => import('@/pages/GameDayDashboard').then((m) => ({ default: m.GameDayDashboard })));
const ChemistryDashboard = lazy(() => import('@/pages/ChemistryDashboard').then((m) => ({ default: m.ChemistryDashboard })));
const Fleet = lazy(() => import('@/pages/Fleet').then((m) => ({ default: m.Fleet })));
const Alerts = lazy(() => import('@/pages/Alerts').then((m) => ({ default: m.Alerts })));
const Experiments = lazy(() => import('@/pages/Experiments').then((m) => ({ default: m.Experiments })));
const ThemeCustomizer = lazy(() => import('@/components/theme/ThemeCustomizer').then((m) => ({ default: m.ThemeCustomizer })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ExportProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Layout />}>
                <Route path="/" element={<Suspense fallback={<PageLoader />}><TelemetryOverview /></Suspense>} />
                <Route path="/scene" element={<Suspense fallback={<PageLoader />}><Scene3D /></Suspense>} />
                <Route path="/simulation" element={<Suspense fallback={<PageLoader />}><Simulation /></Suspense>} />
                <Route path="/chemistry" element={<Suspense fallback={<PageLoader />}><ChemistryDashboard /></Suspense>} />
                <Route path="/detections" element={<Suspense fallback={<PageLoader />}><Detections /></Suspense>} />
                <Route path="/models" element={<Suspense fallback={<PageLoader />}><Models /></Suspense>} />
                <Route path="/ml-analytics" element={<Suspense fallback={<PageLoader />}><MLAnalytics /></Suspense>} />
                <Route path="/test/single" element={<Suspense fallback={<PageLoader />}><SingleImageTest /></Suspense>} />
                <Route path="/test/batch" element={<Suspense fallback={<PageLoader />}><BatchTest /></Suspense>} />
                <Route path="/predictive" element={<Suspense fallback={<PageLoader />}><PredictiveAnalytics /></Suspense>} />
                <Route path="/streaming" element={<Suspense fallback={<PageLoader />}><StreamingDashboard /></Suspense>} />
                <Route path="/drift" element={<Suspense fallback={<PageLoader />}><DriftDashboard /></Suspense>} />
                <Route path="/anomaly" element={<Suspense fallback={<PageLoader />}><AnomalyInvestigation /></Suspense>} />
                <Route path="/gameday" element={<Suspense fallback={<PageLoader />}><GameDayDashboard /></Suspense>} />
                <Route path="/analytics" element={<Suspense fallback={<PageLoader />}><Analytics /></Suspense>} />
                <Route path="/advanced-analytics" element={<Suspense fallback={<PageLoader />}><AdvancedAnalytics /></Suspense>} />
                <Route path="/fleet" element={<Suspense fallback={<PageLoader />}><Fleet /></Suspense>} />
                <Route path="/alerts" element={<Suspense fallback={<PageLoader />}><Alerts /></Suspense>} />
                <Route path="/experiments" element={<Suspense fallback={<PageLoader />}><Experiments /></Suspense>} />
                <Route path="/theme-customizer" element={<Suspense fallback={<PageLoader />}><ThemeCustomizer /></Suspense>} />
              </Route>
            </Routes>
            <ExportDialogGlobal />
            <Toaster theme="dark" position="top-right" />
          </BrowserRouter>
        </ExportProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

function ExportDialogGlobal() {
  const { isOpen, config, closeExport } = useExport();
  return (
    <ExportDialog
      open={isOpen}
      onClose={closeExport}
      {...config}
    />
  );
}

function PageLoader() {
  return (
    <div className="flex h-screen items-center justify-center bg-bg">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-text-tertiary">Loading Module…</span>
      </div>
    </div>
  );
}
