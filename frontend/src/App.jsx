import { Suspense, lazy } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import LoadingState from './components/LoadingState';
import ToastContainer from './components/ToastContainer';

const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ResumeAnalyzerPage = lazy(() => import('./pages/ResumeAnalyzerPage'));
const SkillGapPage = lazy(() => import('./pages/SkillGapPage'));
const CareerPredictionPage = lazy(() => import('./pages/CareerPredictionPage'));
const JobExplorerPage = lazy(() => import('./pages/JobExplorerPage'));
const RoadmapPage = lazy(() => import('./pages/RoadmapPage'));
const ProgressPage = lazy(() => import('./pages/ProgressPage'));
const ProfileSettingsPage = lazy(() => import('./pages/ProfileSettingsPage'));

function PageLoader() {
  return (
    <div className="p-6">
      <LoadingState
        title="Loading workspace..."
        subtitle="Preparing SkillGap AI module"
      />
    </div>
  );
}

export default function App() {
  return (
    <>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public Marketing & Auth Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* SaaS Application Workspace Routes */}
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/resume-analyzer" element={<ResumeAnalyzerPage />} />
            <Route path="/skill-gaps" element={<SkillGapPage />} />
            <Route path="/career-prediction" element={<CareerPredictionPage />} />
            <Route path="/jobs" element={<JobExplorerPage />} />
            <Route path="/roadmap" element={<RoadmapPage />} />
            <Route path="/progress" element={<ProgressPage />} />
            <Route path="/settings" element={<ProfileSettingsPage />} />
          </Route>

          {/* Backward-compatible route redirects from Phase 1 */}
          <Route path="/resume-upload" element={<Navigate to="/resume-analyzer" replace />} />
          <Route path="/job-matcher" element={<Navigate to="/jobs" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>

      <ToastContainer />
    </>
  );
}
