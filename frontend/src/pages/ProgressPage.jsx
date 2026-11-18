import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Award,
  CheckCircle2,
  Circle,
  Clock,
  Flame,
  Plus,
  Target,
  TrendingUp,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import DemoBadge from '../components/DemoBadge';
import MetricCard from '../components/MetricCard';
import { useApp } from '../context/AppContext';
import { updateRoadmapTask } from '../services/api';

export default function ProgressPage() {
  const {
    user,
    userSkills,
    weeklyData,
    logStudySession,
    activeRoadmapStats,
    completedTaskIds,
    toggleRoadmapTask,
    roadmapHorizon,
    liveRoadmap,
    setLiveRoadmap,
    notify,
  } = useApp();

  const [filter, setFilter] = useState('all');
  const [hoursInput, setHoursInput] = useState('2');
  const [topicInput, setTopicInput] = useState('');
  const [togglingId, setTogglingId] = useState(null);

  const latestWeek = weeklyData[weeklyData.length - 1] || { hours: 0, readiness: 0 };
  const totalHours = weeklyData.reduce((acc, w) => acc + w.hours, 0).toFixed(1);
  const goalPct = Math.min(
    100,
    Math.round((latestWeek.hours / (user.weeklyGoalHours || 10)) * 100),
  );

  const isTaskDone = (task) =>
    task.isLive ? Boolean(task.is_completed) : completedTaskIds.includes(task.id);

  const handleToggleTask = async (task) => {
    if (task.isLive && liveRoadmap) {
      setTogglingId(task.id);
      try {
        const res = await updateRoadmapTask(task.id, !task.is_completed);
        setLiveRoadmap((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            progress: res.roadmap_progress,
            phases: prev.phases.map((ph) => {
              const updatedTasks = ph.tasks.map((t) =>
                t.id === task.id
                  ? {
                      ...t,
                      is_completed: res.task.is_completed,
                      completed_at: res.task.completed_at,
                    }
                  : t,
              );
              return {
                ...ph,
                tasks: updatedTasks,
                completed_tasks: updatedTasks.filter((t) => t.is_completed).length,
                is_completed:
                  updatedTasks.length > 0 &&
                  updatedTasks.every((t) => t.is_completed),
              };
            }),
          };
        });
        notify(
          res.task.is_completed
            ? `Completed: ${task.title}`
            : `Reopened: ${task.title}`,
          res.task.is_completed ? 'success' : 'info',
        );
      } catch {
        notify('Failed to save task status to backend', 'error');
      } finally {
        setTogglingId(null);
      }
      return;
    }
    toggleRoadmapTask(task.id, task.title);
  };

  const visibleTasks = activeRoadmapStats.allTasks.filter((t) => {
    const done = isTaskDone(t);
    if (filter === 'completed') return done;
    if (filter === 'pending') return !done;
    return true;
  });

  const activeDuration = activeRoadmapStats.durationDays || roadmapHorizon;

  const skillMasteryData = userSkills.slice(0, 7).map((s) => ({
    name: s.name,
    Proficiency: s.level || 75,
  }));

  const handleLogStudy = (e) => {
    e.preventDefault();
    logStudySession(hoursInput, topicInput.trim() || 'Skill Roadmap Practice');
    setTopicInput('');
  };

  return (
    <div className="space-y-6">
      {/* KPI Strip */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Roadmap Completion"
          value={`${activeRoadmapStats.percent}%`}
          badge={`${activeDuration}d plan`}
          subtitle={`${activeRoadmapStats.completedCount} of ${activeRoadmapStats.totalCount} tasks done`}
          icon={Target}
          accent="indigo"
        />
        <MetricCard
          title="This Week's Study"
          value={`${latestWeek.hours}h`}
          badge={`${goalPct}% of goal`}
          subtitle={`Weekly target: ${user.weeklyGoalHours} hours`}
          icon={Clock}
          accent="blue"
        />
        <MetricCard
          title="Total Logged Hours"
          value={`${totalHours}h`}
          badge="6 weeks"
          subtitle="Steady upward skill velocity"
          icon={TrendingUp}
          accent="purple"
        />
        <MetricCard
          title="Current Streak"
          value="9 Days"
          badge="Active"
          subtitle="Keep logging sessions to extend streak"
          icon={Flame}
          accent="emerald"
        />
      </section>

      {/* Charts Row */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Weekly Study Hours &amp; Readiness Score
              </h3>
              <p className="text-xs text-slate-500">
                Log new study sessions below to update this chart live
              </p>
            </div>
            <DemoBadge />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#475569' }} />
                <YAxis tick={{ fontSize: 11, fill: '#475569' }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Area
                  type="monotone"
                  dataKey="readiness"
                  name="Readiness %"
                  stroke="#4F46E5"
                  fill="#4F46E5"
                  fillOpacity={0.14}
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="hours"
                  name="Study Hours"
                  stroke="#7C3AED"
                  fill="#7C3AED"
                  fillOpacity={0.12}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Top Skill Proficiency Levels
              </h3>
              <p className="text-xs text-slate-500">
                Current confidence estimates across core skills
              </p>
            </div>
            <Link
              to="/settings"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              Manage Skills &rarr;
            </Link>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillMasteryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#475569' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#475569' }} />
                <Tooltip formatter={(v) => [`${v}%`, 'Proficiency']} />
                <Bar
                  dataKey="Proficiency"
                  fill="#2563EB"
                  radius={[6, 6, 0, 0]}
                  maxBarSize={38}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Log Study Session + Interactive Milestone Checklist */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs lg:col-span-4">
          <div className="flex items-center gap-2">
            <Award className="h-4 w-4 text-purple-600" />
            <h3 className="text-sm font-semibold text-slate-900">Log Study Session</h3>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Record completed practice hours to update your weekly velocity and readiness.
          </p>

          <form onSubmit={handleLogStudy} className="mt-5 space-y-4">
            <div>
              <label
                htmlFor="study-topic"
                className="block text-xs font-semibold text-slate-700"
              >
                Topic / Skill Practiced
              </label>
              <input
                id="study-topic"
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                placeholder="e.g., Docker Compose & Alembic"
                className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label
                htmlFor="study-hours"
                className="block text-xs font-semibold text-slate-700"
              >
                Duration (Hours)
              </label>
              <input
                id="study-hours"
                type="number"
                step="0.5"
                min="0.5"
                max="16"
                value={hoursInput}
                onChange={(e) => setHoursInput(e.target.value)}
                className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                required
              />
            </div>

            <button
              type="submit"
              className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4" />
              <span>Log Study Progress</span>
            </button>
          </form>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs lg:col-span-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-sm font-semibold text-slate-900">
                  Milestone Task Tracker ({activeDuration}-Day Roadmap)
                </h3>
                {activeRoadmapStats.isLive && (
                  <DemoBadge mode="live" label="Live DB Synced" />
                )}
              </div>
              <p className="text-xs text-slate-500">
                Toggle tasks directly here or in the AI Learning Roadmap view
              </p>
            </div>

            <div className="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
              {[
                { key: 'all', label: 'All' },
                { key: 'pending', label: 'In Progress' },
                { key: 'completed', label: 'Completed' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setFilter(tab.key)}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    filter === tab.key
                      ? 'bg-white text-indigo-700 shadow-2xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 divide-y divide-slate-100">
            {visibleTasks.length === 0 ? (
              <p className="py-8 text-center text-xs text-slate-500">
                No tasks match this filter right now.
              </p>
            ) : (
              visibleTasks.map((task) => {
                const done = isTaskDone(task);
                return (
                  <label
                    key={task.id}
                    className={`flex cursor-pointer items-center justify-between gap-3 py-3 ${
                      togglingId === task.id ? 'opacity-60' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={done}
                        disabled={togglingId === task.id}
                        onChange={() => handleToggleTask(task)}
                        className="sr-only"
                      />
                      {done ? (
                        <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
                      ) : (
                        <Circle className="h-4 w-4 shrink-0 text-slate-300" />
                      )}
                      <div>
                        <p
                          className={`text-xs font-medium ${
                            done ? 'text-slate-400 line-through' : 'text-slate-900'
                          }`}
                        >
                          {task.title}
                        </p>
                        <p className="text-[11px] text-slate-500">{task.resource}</p>
                      </div>
                    </div>
                    <span
                      className={`shrink-0 rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                        done
                          ? 'bg-emerald-50 text-emerald-700'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {done ? 'Done' : `${task.hours}h`}
                    </span>
                  </label>
                );
              })
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
