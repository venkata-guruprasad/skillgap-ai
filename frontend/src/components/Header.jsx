import { Link, useLocation } from 'react-router-dom';
import { Menu, RefreshCw, Upload } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { formatTimestamp } from '../utils/formatters';

const ROUTE_TITLES = {
  '/dashboard': {
    title: 'Student Dashboard',
    subtitle: 'Overview of your extracted skills, career fit, and roadmap velocity',
  },
  '/resume-analyzer': {
    title: 'Resume Analyzer',
    subtitle: 'Upload your PDF or DOCX resume to inspect extracted skills and ATS signals',
  },
  '/skill-gaps': {
    title: 'Skill Gap Analysis',
    subtitle: 'Benchmark your current skills against target industry roles',
  },
  '/career-prediction': {
    title: 'Career Prediction',
    subtitle: 'Explore ranked career matches, compatibility scores, and gap explanations',
  },
  '/jobs': {
    title: 'Job Explorer',
    subtitle: 'Search curated roles ranked by skill compatibility',
  },
  '/roadmap': {
    title: 'AI Learning Roadmap',
    subtitle: 'Structured 30, 60, and 90-day milestone plans to close skill gaps',
  },
  '/progress': {
    title: 'Progress Tracking',
    subtitle: 'Track weekly study hours, milestone velocity, and skill mastery',
  },
  '/settings': {
    title: 'Profile Settings',
    subtitle: 'Manage your student profile, target role, and verified skills',
  },
};

export default function Header() {
  const { toggleSidebar, health } = useApp();
  const { pathname } = useLocation();
  const routeInfo = ROUTE_TITLES[pathname] || {
    title: 'SkillGap AI',
    subtitle: 'AI-Powered Skill Gap & Career Prediction System',
  };

  const isHealthy = health.apiHealth.status === 'success';
  const isLoading = health.apiHealth.status === 'loading';

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-slate-200/80 bg-white/95 px-4 backdrop-blur-xs lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={toggleSidebar}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="min-w-0">
          <h1 className="truncate text-base font-semibold tracking-tight text-slate-900 sm:text-lg">
            {routeInfo.title}
          </h1>
          <p className="hidden truncate text-xs text-slate-500 md:block">
            {routeInfo.subtitle}
          </p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2.5">
        {/* Live FastAPI health status pill (real API data) */}
        <button
          type="button"
          onClick={health.refresh}
          disabled={health.isRefreshing}
          title={`${health.apiHealth.message} (Last checked: ${formatTimestamp(health.lastChecked)})`}
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition ${
            isLoading
              ? 'border-slate-200 bg-slate-50 text-slate-600'
              : isHealthy
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100/70'
              : 'border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100/70'
          }`}
        >
          <span
            className={`h-2 w-2 rounded-full ${
              isLoading
                ? 'bg-slate-400'
                : isHealthy
                ? 'bg-emerald-500'
                : 'bg-rose-500'
            }`}
          />
          <span className="hidden sm:inline">
            {isLoading ? 'Checking API' : isHealthy ? 'API Live' : 'API Offline'}
          </span>
          <RefreshCw
            className={`h-3 w-3 opacity-75 ${health.isRefreshing ? 'animate-spin' : ''}`}
          />
        </button>

        {pathname !== '/resume-analyzer' && (
          <Link
            to="/resume-analyzer"
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700"
          >
            <Upload className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Analyze Resume</span>
          </Link>
        )}
      </div>
    </header>
  );
}
