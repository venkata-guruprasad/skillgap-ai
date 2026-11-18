import { Link, NavLink, useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Compass,
  FileText,
  GitCompare,
  Home,
  LayoutDashboard,
  LogOut,
  Map,
  Settings,
  TrendingUp,
  X,
} from 'lucide-react';
import logo from '../assets/logo.svg';
import { useApp } from '../context/AppContext';

const navGroups = [
  {
    label: 'Workspace',
    items: [
      { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { to: '/resume-analyzer', label: 'Resume Analyzer', icon: FileText },
      { to: '/skill-gaps', label: 'Skill Gap Analysis', icon: GitCompare },
    ],
  },
  {
    label: 'Career Intelligence',
    items: [
      { to: '/career-prediction', label: 'Career Prediction', icon: Compass },
      { to: '/jobs', label: 'Job Explorer', icon: Briefcase },
    ],
  },
  {
    label: 'Growth',
    items: [
      { to: '/roadmap', label: 'AI Learning Roadmap', icon: Map },
      { to: '/progress', label: 'Progress Tracking', icon: TrendingUp },
    ],
  },
  {
    label: 'Account',
    items: [{ to: '/settings', label: 'Profile Settings', icon: Settings }],
  },
];

export default function Sidebar() {
  const { appName, sidebarOpen, setSidebarOpen, user, logout, activeRoadmapStats } =
    useApp();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setSidebarOpen(false);
    navigate('/login');
  };

  const initials = (user.fullName || 'AR')
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-950/50 backdrop-blur-[1px] lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col border-r border-slate-800/80 bg-[#0B1120] text-slate-300 transition-transform duration-200 lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800/80 px-5">
          <Link
            to="/"
            className="flex items-center gap-3 rounded-lg focus:outline-none"
            onClick={() => setSidebarOpen(false)}
          >
            <img src={logo} alt="SkillGap AI" className="h-8 w-8 rounded-lg" />
            <div>
              <span className="block text-sm font-bold tracking-tight text-white">
                {appName}
              </span>
              <span className="block text-[11px] text-slate-400">
                Career Intelligence
              </span>
            </div>
          </Link>

          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation groups */}
        <nav className="sidebar-scroll flex-1 space-y-6 overflow-y-auto px-3 py-5">
          {navGroups.map((group) => (
            <div key={group.label}>
              <p className="mb-2 px-3 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
                {group.label}
              </p>
              <div className="space-y-0.5">
                {group.items.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-indigo-500/15 text-white shadow-[inset_2px_0_0_0_#6366F1]'
                          : 'text-slate-400 hover:bg-slate-800/70 hover:text-slate-100'
                      }`
                    }
                  >
                    <Icon className="h-4 w-4 shrink-0 text-current opacity-85" />
                    <span className="truncate">{label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Mini roadmap progress widget */}
        <div className="mx-3 mb-3 rounded-xl border border-slate-800 bg-slate-900/70 p-3.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-medium text-slate-200">Roadmap Progress</span>
            <span className="font-semibold text-indigo-400 tabular-nums">
              {activeRoadmapStats.percent}%
            </span>
          </div>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
            <div
              className="h-full rounded-full bg-indigo-500 transition-all duration-300"
              style={{ width: `${activeRoadmapStats.percent}%` }}
            />
          </div>
          <p className="mt-2 text-[11px] text-slate-400">
            {activeRoadmapStats.completedCount} of {activeRoadmapStats.totalCount} tasks done
          </p>
        </div>

        {/* User profile footer */}
        <div className="border-t border-slate-800/80 p-3">
          <div className="flex items-center gap-3 rounded-lg px-2 py-2">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-semibold text-white">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-white">
                {user.fullName}
              </p>
              <p className="truncate text-[11px] text-slate-400">{user.email}</p>
            </div>
          </div>

          <div className="mt-2 flex items-center gap-1.5">
            <Link
              to="/"
              onClick={() => setSidebarOpen(false)}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-slate-800 px-2.5 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              <Home className="h-3.5 w-3.5" />
              <span>Home</span>
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-slate-800 px-2.5 py-1.5 text-xs font-medium text-slate-300 transition hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-300"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
