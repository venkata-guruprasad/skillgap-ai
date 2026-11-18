import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  AlertCircle,
  Award,
  BookOpen,
  Calendar,
  CheckCircle2,
  Circle,
  Clock,
  ExternalLink,
  FolderGit2,
  History,
  ListChecks,
  Loader2,
  Lock,
  RefreshCw,
  Sparkles,
  Target,
  Wrench,
} from 'lucide-react';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import { useApp } from '../context/AppContext';
import {
  fetchRoadmapDetail,
  fetchRoadmaps,
  generateRoadmap,
  updateRoadmapTask,
} from '../services/api';

const CAREER_ROLE_OPTIONS = [
  'Data Analyst',
  'Data Scientist',
  'Machine Learning Engineer',
  'Python Developer',
  'Full Stack Developer',
  'Backend Developer',
  'Frontend Developer',
  'AI Engineer',
  'Business Analyst',
  'Data Engineer',
  'Cloud Engineer',
  'Cybersecurity Analyst',
];

const DURATIONS = [30, 60, 90];

const TASK_TYPE_STYLES = {
  study: 'bg-blue-50 text-blue-700 border-blue-200',
  exercise: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  mini_project: 'bg-purple-50 text-purple-700 border-purple-200',
  checkpoint: 'bg-emerald-50 text-emerald-700 border-emerald-200',
};

export default function RoadmapPage() {
  const {
    authToken,
    login,
    userSkills,
    latestSkillGapAnalysis,
    liveRoadmap,
    setLiveRoadmap,
    notify,
  } = useApp();

  const [searchParams] = useSearchParams();
  const initialRoleParam = searchParams.get('role');

  const [targetRole, setTargetRole] = useState(
    initialRoleParam && CAREER_ROLE_OPTIONS.includes(initialRoleParam)
      ? initialRoleParam
      : latestSkillGapAnalysis?.job_title &&
        CAREER_ROLE_OPTIONS.includes(latestSkillGapAnalysis.job_title)
      ? latestSkillGapAnalysis.job_title
      : 'Machine Learning Engineer',
  );
  const [durationDays, setDurationDays] = useState(30);
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [learningStyle, setLearningStyle] = useState('balanced');
  const [focusSkillsInput, setFocusSkillsInput] = useState('');

  const [roadmaps, setRoadmaps] = useState([]);
  const [activeRoadmap, setActiveRoadmap] = useState(liveRoadmap);
  const [loadingInit, setLoadingInit] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [updatingTaskId, setUpdatingTaskId] = useState(null);
  const [authenticatingDemo, setAuthenticatingDemo] = useState(false);
  const [error, setError] = useState('');

  const loadRoadmaps = useCallback(async () => {
    if (!authToken) {
      setLoadingInit(false);
      return;
    }
    setLoadingInit(true);
    setError('');
    try {
      const list = await fetchRoadmaps();
      setRoadmaps(list.items || []);
      const targetId = list.active_roadmap_id || list.items?.[0]?.id;
      if (targetId) {
        const detail = await fetchRoadmapDetail(targetId);
        setActiveRoadmap(detail);
        setLiveRoadmap(detail);
        setDurationDays(detail.duration_days);
        if (!initialRoleParam && CAREER_ROLE_OPTIONS.includes(detail.target_role)) {
          setTargetRole(detail.target_role);
        }
      }
    } catch {
      setError('Unable to load learning roadmaps from the backend API.');
    } finally {
      setLoadingInit(false);
    }
  }, [authToken, initialRoleParam, setLiveRoadmap]);

  useEffect(() => {
    loadRoadmaps();
  }, [authToken]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleQuickDemoSignIn = async () => {
    setAuthenticatingDemo(true);
    setError('');
    try {
      await login('alex.rivera@university.edu', 'demo-password-2026');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Demo sign-in failed.');
    } finally {
      setAuthenticatingDemo(false);
    }
  };

  const handleGenerateRoadmap = async (overrideDuration) => {
    const selectedDuration = overrideDuration || durationDays;
    if (!authToken) {
      setError('Sign in first to generate and save a personalized roadmap.');
      return;
    }

    setGenerating(true);
    setError('');
    try {
      const focusSkills = focusSkillsInput
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      const payload = {
        target_role: targetRole,
        duration_days: selectedDuration,
        resume_skills: userSkills.map((s) => s.name),
        weekly_hours: Number(weeklyHours) || 10,
        learning_style: learningStyle,
        focus_skills: focusSkills,
      };
      if (latestSkillGapAnalysis?.id && latestSkillGapAnalysis.job_title === targetRole) {
        payload.analysis_id = latestSkillGapAnalysis.id;
      }

      const created = await generateRoadmap(payload);
      setActiveRoadmap(created);
      setLiveRoadmap(created);
      setDurationDays(created.duration_days);
      notify(`Generated ${created.duration_days}-day roadmap for ${created.target_role}`);

      const list = await fetchRoadmaps();
      setRoadmaps(list.items || []);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Failed to generate learning roadmap. Verify backend status.',
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectHistoryRoadmap = async (roadmapId) => {
    setError('');
    try {
      const detail = await fetchRoadmapDetail(roadmapId);
      setActiveRoadmap(detail);
      setLiveRoadmap(detail);
      setDurationDays(detail.duration_days);
      if (CAREER_ROLE_OPTIONS.includes(detail.target_role)) {
        setTargetRole(detail.target_role);
      }
      notify(`Resumed "${detail.title}"`, 'info');
    } catch {
      setError('Unable to load selected roadmap.');
    }
  };

  const handleToggleTask = async (task) => {
    if (!authToken || updatingTaskId === task.id) return;
    setUpdatingTaskId(task.id);
    setError('');

    const nextCompleted = !task.is_completed;
    try {
      const res = await updateRoadmapTask(task.id, nextCompleted);
      if (activeRoadmap) {
        const updatedPhases = activeRoadmap.phases.map((phase) => {
          if (phase.phase_number !== task.phase_number) return phase;
          const updatedTasks = phase.tasks.map((t) =>
            t.id === task.id ? res.task : t,
          );
          const doneCount = updatedTasks.filter((t) => t.is_completed).length;
          return {
            ...phase,
            tasks: updatedTasks,
            completed_tasks: doneCount,
            is_completed: updatedTasks.length > 0 && doneCount === updatedTasks.length,
          };
        });
        const nextRoadmap = {
          ...activeRoadmap,
          progress: res.roadmap_progress,
          phases: updatedPhases,
        };
        setActiveRoadmap(nextRoadmap);
        setLiveRoadmap(nextRoadmap);
      }

      setRoadmaps((prev) =>
        prev.map((rm) =>
          rm.id === task.roadmap_id ? { ...rm, progress: res.roadmap_progress } : rm,
        ),
      );
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to update task completion.');
    } finally {
      setUpdatingTaskId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Auth Gate Notice */}
      {!authToken && (
        <section className="flex flex-col justify-between gap-4 rounded-2xl border border-amber-200 bg-amber-50/80 p-5 sm:flex-row sm:items-center">
          <div className="flex items-start gap-3">
            <Lock className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            <div>
              <h2 className="text-sm font-semibold text-amber-950">
                Sign in to generate and save Personalized AI Learning Roadmaps
              </h2>
              <p className="mt-0.5 text-xs text-amber-800">
                Your 30, 60, and 90-day roadmaps, completed tasks, and learning history are
                persisted securely in the backend database.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleQuickDemoSignIn}
            disabled={authenticatingDemo}
            className="shrink-0 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
          >
            {authenticatingDemo ? 'Signing in...' : 'Sign In (Demo Student)'}
          </button>
        </section>
      )}

      {/* Generator & 30/60/90-Day Controls */}
      <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">
                Personalized AI Learning Roadmap Generator
              </h2>
              <DemoBadge mode="live" label="Live Persisted Roadmap API" />
              {activeRoadmap && (
                <span className="rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-0.5 text-[11px] font-semibold text-indigo-700">
                  Engine:{' '}
                  {activeRoadmap.generation_mode === 'deterministic'
                    ? 'Deterministic Curated Engine'
                    : activeRoadmap.generation_mode}
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Tailors weekly tasks, practical exercises, mini projects, checkpoints, and
              verified resources to close your missing skills for your target career role.
            </p>
          </div>

          {/* 30 / 60 / 90 Day Selector */}
          <div className="inline-flex shrink-0 rounded-xl border border-slate-200 bg-slate-100 p-1">
            {DURATIONS.map((days) => (
              <button
                key={days}
                type="button"
                onClick={() => setDurationDays(days)}
                className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                  durationDays === days
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {days} Days
              </button>
            ))}
          </div>
        </div>

        {/* Customization Form Row */}
        <div className="mt-5 grid grid-cols-1 gap-3 rounded-xl border border-slate-200/80 bg-[#F8FAFC] p-4 md:grid-cols-12 md:items-end">
          <div className="md:col-span-3">
            <label className="block text-xs font-semibold text-slate-700">
              Target Career Role
            </label>
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            >
              {CAREER_ROLE_OPTIONS.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-slate-700">
              Hours / Week
            </label>
            <input
              type="number"
              min={2}
              max={45}
              value={weeklyHours}
              onChange={(e) => setWeeklyHours(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-slate-700">
              Learning Style
            </label>
            <select
              value={learningStyle}
              onChange={(e) => setLearningStyle(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            >
              <option value="balanced">Balanced</option>
              <option value="project-heavy">Project-Heavy</option>
              <option value="fundamentals-first">Fundamentals-First</option>
            </select>
          </div>

          <div className="md:col-span-3">
            <label className="block text-xs font-semibold text-slate-700">
              Priority Focus Skills (Optional)
            </label>
            <input
              type="text"
              value={focusSkillsInput}
              onChange={(e) => setFocusSkillsInput(e.target.value)}
              placeholder="e.g., Docker, PyTorch"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="md:col-span-2">
            <button
              type="button"
              onClick={() => handleGenerateRoadmap()}
              disabled={generating || !authToken}
              className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  {activeRoadmap ? (
                    <RefreshCw className="h-3.5 w-3.5" />
                  ) : (
                    <Sparkles className="h-3.5 w-3.5" />
                  )}
                  <span>{activeRoadmap ? 'Regenerate' : 'Generate'}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-medium text-rose-700">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </section>

      {/* Learning History Strip */}
      {authToken && roadmaps.length > 0 && (
        <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-indigo-600" />
            <h3 className="text-sm font-semibold text-slate-900">
              Your Learning History ({roadmaps.length} saved roadmaps)
            </h3>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-2.5 md:grid-cols-2 lg:grid-cols-3">
            {roadmaps.slice(0, 6).map((rm) => {
              const selected = activeRoadmap?.id === rm.id;
              return (
                <button
                  key={rm.id}
                  type="button"
                  onClick={() => handleSelectHistoryRoadmap(rm.id)}
                  className={`flex items-center justify-between rounded-xl border p-3 text-left transition ${
                    selected
                      ? 'border-indigo-400 bg-indigo-50/60'
                      : 'border-slate-200 bg-[#F8FAFC] hover:border-slate-300'
                  }`}
                >
                  <div className="min-w-0">
                    <p className="truncate text-xs font-semibold text-slate-900">
                      {rm.title}
                    </p>
                    <p className="mt-0.5 text-[11px] text-slate-500">
                      {rm.progress.completed_tasks}/{rm.progress.total_tasks} tasks ·{' '}
                      {rm.progress.completed_milestones}/{rm.progress.total_milestones}{' '}
                      milestones
                    </p>
                  </div>
                  <span className="ml-2 shrink-0 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-bold text-indigo-700 tabular-nums">
                    {Math.round(rm.progress.progress_percent)}%
                  </span>
                </button>
              );
            })}
          </div>
        </section>
      )}

      {/* Active Roadmap Progress & Timeline */}
      {loadingInit ? (
        <div className="flex items-center justify-center rounded-2xl border border-slate-200 bg-white py-14 text-xs text-slate-500">
          <Loader2 className="mr-2 h-4 w-4 animate-spin text-indigo-600" />
          Loading your learning roadmap...
        </div>
      ) : !activeRoadmap ? (
        <EmptyState
          icon={Target}
          title="Generate your personalized AI Learning Roadmap"
          description={`Choose your target role (${targetRole}) and duration (${durationDays} Days) above, then click Generate to create a persisted roadmap with verified learning resources.`}
          actionLabel={generating ? 'Generating...' : `Generate ${durationDays}-Day Roadmap`}
          onAction={() => handleGenerateRoadmap()}
        />
      ) : (
        <div className="space-y-6">
          {/* Active Roadmap Overview & Progress Bar */}
          <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">
                    {activeRoadmap.duration_days}-Day Plan ({activeRoadmap.estimated_weeks}{' '}
                    Weeks)
                  </span>
                  <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
                    Target: {activeRoadmap.target_role}
                  </span>
                </div>
                <h3 className="mt-2 text-xl font-bold text-slate-950">
                  {activeRoadmap.title}
                </h3>
                <p className="mt-1.5 max-w-3xl text-xs leading-relaxed text-slate-600">
                  {activeRoadmap.summary_explanation}
                </p>
              </div>
            </div>

            {/* Persisted Progress Bar */}
            <div className="mt-5 rounded-xl border border-slate-200/80 bg-[#F8FAFC] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex flex-wrap items-center gap-4">
                  <span className="font-semibold text-slate-900">
                    Persisted Learning Progress
                  </span>
                  <span className="inline-flex items-center gap-1 text-slate-600">
                    <ListChecks className="h-3.5 w-3.5 text-indigo-600" />
                    {activeRoadmap.progress.completed_tasks} /{' '}
                    {activeRoadmap.progress.total_tasks} tasks completed
                  </span>
                  <span className="inline-flex items-center gap-1 text-slate-600">
                    <Award className="h-3.5 w-3.5 text-emerald-600" />
                    {activeRoadmap.progress.completed_milestones} /{' '}
                    {activeRoadmap.progress.total_milestones} milestones finished
                  </span>
                  <span className="inline-flex items-center gap-1 text-slate-600">
                    <Clock className="h-3.5 w-3.5 text-slate-400" />
                    {activeRoadmap.progress.remaining_hours}h remaining (of{' '}
                    {activeRoadmap.progress.total_hours}h)
                  </span>
                </div>
                <span className="text-sm font-bold text-indigo-600 tabular-nums">
                  {activeRoadmap.progress.progress_percent}%
                </span>
              </div>

              <div className="mt-2.5 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
                <div
                  className="h-full rounded-full bg-indigo-600 transition-all duration-300"
                  style={{ width: `${activeRoadmap.progress.progress_percent}%` }}
                />
              </div>
            </div>
          </section>

          {/* Visual Vertical Timeline of Learning Phases */}
          <section className="relative space-y-6 pl-0 md:pl-8">
            <div
              className="absolute top-6 bottom-6 left-3.5 hidden w-0.5 bg-slate-200 md:block"
              aria-hidden="true"
            />

            {activeRoadmap.phases.map((phase) => {
              const phasePct =
                phase.total_tasks > 0
                  ? Math.round((phase.completed_tasks / phase.total_tasks) * 100)
                  : 0;

              return (
                <div key={phase.phase_number} className="relative">
                  <div
                    className={`absolute top-6 -left-8 hidden h-7 w-7 items-center justify-center rounded-full border-2 text-xs font-bold md:flex ${
                      phase.is_completed
                        ? 'border-emerald-500 bg-emerald-500 text-white'
                        : 'border-indigo-500 bg-white text-indigo-700'
                    }`}
                  >
                    {phase.phase_number}
                  </div>

                  <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
                    {/* Phase Header */}
                    <div className="flex flex-col justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold text-slate-700">
                            <Calendar className="h-3 w-3" />
                            {phase.timeframe}
                          </span>
                          <span className="rounded-md bg-purple-50 px-2.5 py-0.5 text-[11px] font-semibold text-purple-700">
                            Skill: {phase.skill_name}
                          </span>
                          <span className="rounded-md bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700">
                            {phase.priority} · ~{phase.estimated_hours}h
                          </span>
                        </div>
                        <h4 className="mt-2 text-base font-bold text-slate-950">
                          {phase.title}
                        </h4>
                      </div>

                      <div className="shrink-0 text-left sm:text-right">
                        <span className="text-xs font-bold text-slate-900 tabular-nums">
                          {phase.completed_tasks}/{phase.total_tasks} tasks done
                        </span>
                        <div className="mt-1.5 h-1.5 w-32 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${
                              phase.is_completed ? 'bg-emerald-500' : 'bg-indigo-600'
                            }`}
                            style={{ width: `${phasePct}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Learning Objectives */}
                    <div className="mt-4">
                      <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                        Learning Objectives
                      </p>
                      <ul className="mt-1.5 space-y-1 text-xs text-slate-700">
                        {phase.learning_objectives.map((obj, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-500" />
                            <span>{obj}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Weekly Learning Tasks (Interactive Persisted Checkboxes) */}
                    <div className="mt-5">
                      <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                        Weekly Learning Tasks
                      </p>
                      <ul className="mt-2 space-y-2.5">
                        {phase.tasks.map((task) => {
                          const isBusy = updatingTaskId === task.id;
                          return (
                            <li key={task.id}>
                              <label
                                className={`flex cursor-pointer items-start justify-between gap-3 rounded-xl border p-3.5 transition ${
                                  task.is_completed
                                    ? 'border-emerald-200 bg-emerald-50/40'
                                    : 'border-slate-200/80 bg-[#F8FAFC] hover:border-indigo-200 hover:bg-white'
                                }`}
                              >
                                <div className="flex items-start gap-3">
                                  <input
                                    type="checkbox"
                                    checked={task.is_completed}
                                    disabled={isBusy}
                                    onChange={() => handleToggleTask(task)}
                                    className="sr-only"
                                  />
                                  {isBusy ? (
                                    <Loader2 className="mt-0.5 h-5 w-5 shrink-0 animate-spin text-indigo-600" />
                                  ) : task.is_completed ? (
                                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
                                  ) : (
                                    <Circle className="mt-0.5 h-5 w-5 shrink-0 text-slate-300" />
                                  )}
                                  <div>
                                    <div className="flex flex-wrap items-center gap-2">
                                      <span className="text-[11px] font-semibold text-indigo-600">
                                        {task.week_label}
                                      </span>
                                      <span
                                        className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold capitalize ${
                                          TASK_TYPE_STYLES[task.task_type] ||
                                          TASK_TYPE_STYLES.study
                                        }`}
                                      >
                                        {task.task_type.replace('_', ' ')}
                                      </span>
                                    </div>
                                    <span
                                      className={`mt-1 block text-xs font-semibold sm:text-sm ${
                                        task.is_completed
                                          ? 'text-slate-500 line-through'
                                          : 'text-slate-900'
                                      }`}
                                    >
                                      {task.title}
                                    </span>
                                    {task.description && (
                                      <p className="mt-0.5 text-xs text-slate-500">
                                        {task.description}
                                      </p>
                                    )}
                                  </div>
                                </div>

                                <span className="shrink-0 rounded-md bg-white px-2.5 py-1 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200 tabular-nums">
                                  {task.estimated_hours}h
                                </span>
                              </label>
                            </li>
                          );
                        })}
                      </ul>
                    </div>

                    {/* Practical Exercises, Mini Project & Assessment Checkpoint */}
                    <div className="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-3">
                      <div className="rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-3.5">
                        <p className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-800 uppercase">
                          <Wrench className="h-3.5 w-3.5 text-blue-600" />
                          Practical Exercises
                        </p>
                        <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
                          {phase.practical_exercises.map((ex, i) => (
                            <li key={i}>{ex}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="rounded-xl border border-purple-100 bg-purple-50/40 p-3.5">
                        <p className="flex items-center gap-1.5 text-[11px] font-semibold text-purple-900 uppercase">
                          <FolderGit2 className="h-3.5 w-3.5 text-purple-600" />
                          Mini Project
                        </p>
                        <p className="mt-2 text-xs leading-relaxed text-slate-700">
                          {phase.mini_project}
                        </p>
                      </div>

                      <div className="rounded-xl border border-emerald-100 bg-emerald-50/40 p-3.5">
                        <p className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-900 uppercase">
                          <Award className="h-3.5 w-3.5 text-emerald-600" />
                          Assessment Checkpoint
                        </p>
                        <p className="mt-2 text-xs leading-relaxed text-slate-700">
                          {phase.assessment_checkpoint}
                        </p>
                      </div>
                    </div>

                    {/* Verified Trusted Learning Resource Links */}
                    <div className="mt-5 border-t border-slate-100 pt-4">
                      <p className="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                        <BookOpen className="h-3.5 w-3.5 text-indigo-600" />
                        Verified Learning Resources
                      </p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {phase.resources.map((res) => (
                          <a
                            key={res.url}
                            href={res.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700"
                          >
                            <span>{res.title}</span>
                            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500">
                              {res.source}
                            </span>
                            <ExternalLink className="h-3 w-3 text-slate-400" />
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </section>
        </div>
      )}
    </div>
  );
}
