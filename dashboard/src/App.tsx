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
const ReactorDashboard = lazy(() => import('@/pages/ReactorDashboard').then((m) => ({ default: m.ReactorDashboard })));
const LabDashboard = lazy(() => import('@/pages/LabDashboard').then((m) => ({ default: m.LabDashboard })));
const CompChemDashboard = lazy(() => import('@/pages/CompChemDashboard').then((m) => ({ default: m.CompChemDashboard })));
const SSMLDashboard = lazy(() => import('@/pages/SSMLDashboard').then((m) => ({ default: m.SSMLDashboard })));
const MvpDemoDashboard = lazy(() => import('@/pages/MvpDemoDashboard').then((m) => ({ default: m.MvpDemoDashboard })));
// Demo story sub-pages
const DemoLanding = lazy(() => import('@/pages/demo/DemoLanding').then((m) => ({ default: m.DemoLanding })));
const DemoTour = lazy(() => import('@/pages/demo/DemoTour').then((m) => ({ default: m.DemoTour })));
const ProblemView = lazy(() => import('@/pages/demo/ProblemView').then((m) => ({ default: m.ProblemView })));
const ApproachView = lazy(() => import('@/pages/demo/ApproachView').then((m) => ({ default: m.ApproachView })));
const SolventPortfolio = lazy(() => import('@/pages/demo/SolventPortfolio').then((m) => ({ default: m.SolventPortfolio })));
const Solv237Detail = lazy(() => import('@/pages/demo/Solv237Detail').then((m) => ({ default: m.Solv237Detail })));
const ROIView = lazy(() => import('@/pages/demo/ROIView').then((m) => ({ default: m.ROIView })));
const PlatformView = lazy(() => import('@/pages/demo/PlatformView').then((m) => ({ default: m.PlatformView })));
const ValidationView = lazy(() => import('@/pages/demo/ValidationView').then((m) => ({ default: m.ValidationView })));
const ComparisonView = lazy(() => import('@/pages/demo/ComparisonView').then((m) => ({ default: m.ComparisonView })));
const ContactView = lazy(() => import('@/pages/demo/ContactView').then((m) => ({ default: m.ContactView })));
const Fleet = lazy(() => import('@/pages/Fleet').then((m) => ({ default: m.Fleet })));
const Alerts = lazy(() => import('@/pages/Alerts').then((m) => ({ default: m.Alerts })));
const Experiments = lazy(() => import('@/pages/Experiments').then((m) => ({ default: m.Experiments })));
const ThemeCustomizer = lazy(() => import('@/components/theme/ThemeCustomizer').then((m) => ({ default: m.ThemeCustomizer })));
const PublicLanding = lazy(() => import('@/pages/PublicLanding').then((m) => ({ default: m.PublicLanding })));
const PricingPage = lazy(() => import('@/pages/Pricing').then((m) => ({ default: m.PricingPage })));
const BlogIndex = lazy(() => import('@/pages/BlogIndex').then((m) => ({ default: m.BlogIndex })));

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
                <Route path="/reactor" element={<Suspense fallback={<PageLoader />}><ReactorDashboard /></Suspense>} />
                <Route path="/lab" element={<Suspense fallback={<PageLoader />}><LabDashboard /></Suspense>} />
                <Route path="/demo" element={<Suspense fallback={<PageLoader />}><DemoLanding /></Suspense>} />
                <Route path="/demo/tour" element={<Suspense fallback={<PageLoader />}><DemoTour /></Suspense>} />
                <Route path="/demo/problem" element={<Suspense fallback={<PageLoader />}><ProblemView /></Suspense>} />
                <Route path="/demo/approach" element={<Suspense fallback={<PageLoader />}><ApproachView /></Suspense>} />
                <Route path="/demo/portfolio" element={<Suspense fallback={<PageLoader />}><SolventPortfolio /></Suspense>} />
                <Route path="/demo/solv-237" element={<Suspense fallback={<PageLoader />}><Solv237Detail /></Suspense>} />
                <Route path="/demo/roi" element={<Suspense fallback={<PageLoader />}><ROIView /></Suspense>} />
                <Route path="/demo/platform" element={<Suspense fallback={<PageLoader />}><PlatformView /></Suspense>} />
                <Route path="/demo/validation" element={<Suspense fallback={<PageLoader />}><ValidationView /></Suspense>} />
                <Route path="/demo/comparison" element={<Suspense fallback={<PageLoader />}><ComparisonView /></Suspense>} />
                <Route path="/demo/contact" element={<Suspense fallback={<PageLoader />}><ContactView /></Suspense>} />
                <Route path="/demo/overview" element={<Suspense fallback={<PageLoader />}><MvpDemoDashboard /></Suspense>} />
                <Route path="/compchem" element={<Suspense fallback={<PageLoader />}><CompChemDashboard /></Suspense>} />
                <Route path="/ssml" element={<Suspense fallback={<PageLoader />}><SSMLDashboard /></Suspense>} />
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
                <Route path="/landing" element={<Suspense fallback={<PageLoader />}><PublicLanding /></Suspense>} />
                <Route path="/pricing" element={<Suspense fallback={<PageLoader />}><PricingPage /></Suspense>} />
                <Route path="/blog" element={<Suspense fallback={<PageLoader />}><BlogIndex /></Suspense>} />
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
