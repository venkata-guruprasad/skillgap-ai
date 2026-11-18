import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Compass,
  FileText,
  Layers,
  Map,
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
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import DemoBadge from '../components/DemoBadge';
import MetricCard from '../components/MetricCard';
import { useApp } from '../context/AppContext';
import { RADAR_BENCHMARK_DATA } from '../data/demoData';

export default function DashboardPage() {
  const {
    authToken,
    user,
    userSkills,
    resumeSummary,
    latestSkillGapAnalysis,
    dashboardAnalytics,
    refreshDashboardAnalytics,
    targetRole,
    targetRoleComparison,
    careerPredictions,
    activeRoadmapStats,
    weeklyData,
    recentActivity,
    health,
  } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    if (authToken) {
      refreshDashboardAnalytics();
    }
  }, [authToken, refreshDashboardAnalytics]);

  const hasLiveGap = Boolean(latestSkillGapAnalysis);
  const hasLiveCareer =
    Boolean(dashboardAnalytics?.latest_career_recommendations?.length);
  const liveRoadmapSummary = dashboardAnalytics?.active_roadmap || null;
  const liveResume = dashboardAnalytics?.latest_resume || null;

  const compatibilityScore = hasLiveGap
    ? latestSkillGapAnalysis.compatibility_score
    : targetRoleComparison.score;

  const matchedRequiredCount = hasLiveGap
    ? latestSkillGapAnalysis.matched_required_skills.length
    : targetRoleComparison.matched.length;

  const missingRequiredList = hasLiveGap
    ? latestSkillGapAnalysis.missing_required_skills.map((s) => s.skill)
    : targetRoleComparison.missing.map((s) => s.name);

  const activeRoleTitle = hasLiveGap
    ? latestSkillGapAnalysis.job_title
    : liveRoadmapSummary?.target_role || targetRole.title;

  const displayedResumeName = liveResume?.file_name || resumeSummary?.fileName || null;
  const displayedResumeMeta = liveResume
    ? `${liveResume.file_type} · ATS ${liveResume.ats_score}/100 · ${liveResume.technical_skill_count} skills`
    : resumeSummary
    ? `${resumeSummary.fileType} · ATS ${resumeSummary.atsScore}/100 · ${userSkills.length} skills`
    : null;

  const displayedRoadmapPct = liveRoadmapSummary
    ? Math.round(liveRoadmapSummary.progress_percent)
    : activeRoadmapStats.percent;
  const displayedRoadmapDone = liveRoadmapSummary
    ? liveRoadmapSummary.completed_tasks
    : activeRoadmapStats.completedCount;
  const displayedRoadmapTotal = liveRoadmapSummary
    ? liveRoadmapSummary.total_tasks
    : activeRoadmapStats.totalCount;
  const displayedRoadmapRemaining = liveRoadmapSummary
    ? liveRoadmapSummary.remaining_hours
    : activeRoadmapStats.remainingHours;

  const radarChartData =
    hasLiveGap && latestSkillGapAnalysis.radar_data?.length >= 3
      ? latestSkillGapAnalysis.radar_data.map((d) => ({
          domain: d.domain,
          student: d.candidate,
          benchmark: d.required,
        }))
      : RADAR_BENCHMARK_DATA;

  const skillGapChartData = hasLiveGap
    ? (latestSkillGapAnalysis.category_breakdown || []).map((c) => ({
        category: c.category,
        Matched: c.matched_required,
        Missing: c.missing_required,
      }))
    : Array.from(new Set(targetRole.requiredSkills.map((s) => s.category))).map(
        (category) => ({
          category,
          Matched: targetRoleComparison.matched.filter((s) => s.category === category)
            .length,
          Missing: targetRoleComparison.missing.filter((s) => s.category === category)
            .length,
        }),
      );

  const careerCompatibilityData = hasLiveCareer
    ? dashboardAnalytics.latest_career_recommendations.slice(0, 5).map((r) => ({
        role: r.career_title.replace(' Engineer', ' Eng.').replace(' Developer', ' Dev.'),
        compatibility: r.compatibility_score,
      }))
    : careerPredictions.slice(0, 5).map((r) => ({
        role: r.title.replace(' Software ', ' ').replace(' Engineer', ' Eng.'),
        compatibility: r.compatibility,
      }));

  const recommendedRolesList = hasLiveCareer
    ? dashboardAnalytics.latest_career_recommendations.slice(0, 4).map((r) => ({
        id: r.career_title,
        title: r.career_title,
        avgSalary: r.avg_salary || r.category,
        compatibility: r.compatibility_score,
        matchedCount: r.matching_skills.length,
        missingCount: r.missing_skills.length,
        gapLink: r.linked_job_id ? `/skill-gaps?jobId=${r.linked_job_id}` : '/skill-gaps',
      }))
    : careerPredictions.slice(0, 4).map((r) => ({
        id: r.id,
        title: r.title,
        avgSalary: r.avgSalary,
        compatibility: r.compatibility,
        matchedCount: r.matchedSkills.length,
        missingCount: r.missingSkills.length,
        gapLink: '/skill-gaps',
      }));

  const displayedActivity =
    dashboardAnalytics?.recent_activity?.length > 0
      ? dashboardAnalytics.recent_activity.map((item) => ({
          id: item.id,
          title: item.title,
          detail: item.detail,
          timestamp: new Date(item.timestamp).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
          }),
        }))
      : recentActivity;

  return (
    <div className="space-y-6">
      {/* Welcome Banner + Resume Summary */}
      <section className="flex flex-col justify-between gap-5 rounded-2xl border border-slate-200/80 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)] lg:flex-row lg:items-center">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            {hasLiveGap ? (
              <DemoBadge mode="live" label="Live Skill Gap Data" />
            ) : (
              <DemoBadge mode="demo" label="Run Skill Gap for Live Analytics" />
            )}
            <DemoBadge
              mode="live"
              label={
                health.apiHealth.status === 'success'
                  ? 'FastAPI Health: OK'
                  : 'FastAPI Health: Offline'
              }
            />
          </div>
          <h2 className="mt-3 text-2xl font-bold tracking-tight text-slate-950">
            Welcome back, {user.fullName.split(' ')[0]}
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Active benchmark:{' '}
            <span className="font-semibold text-indigo-600">{activeRoleTitle}</span>.{' '}
            {hasLiveGap
              ? latestSkillGapAnalysis.score_explanation.summary_text
              : `Matching ${matchedRequiredCount} of ${targetRole.requiredSkills.length} required skills.`}
          </p>
        </div>

        <div className="flex flex-col gap-3 rounded-xl border border-slate-200/80 bg-[#F8FAFC] p-4 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
              <FileText className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-900">
                {displayedResumeName || 'No resume uploaded yet'}
              </p>
              <p className="text-xs text-slate-500">
                {displayedResumeMeta || 'Upload a PDF or DOCX to extract skills'}
              </p>
            </div>
          </div>
          <Link
            to="/resume-analyzer"
            className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700"
          >
            <span>{displayedResumeName ? 'Open Analyzer' : 'Upload'}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </section>

      {/* Primary KPI Metric Cards */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Overall Compatibility"
          value={`${compatibilityScore}%`}
          badge={hasLiveGap ? 'Weighted' : 'Preview'}
          subtitle={`Role: ${activeRoleTitle}`}
          icon={Target}
          accent="indigo"
          onClick={() => navigate('/skill-gaps')}
        />
        <MetricCard
          title="Extracted Skills"
          value={userSkills.length}
          badge={hasLiveGap ? `${matchedRequiredCount} matched` : 'Profile'}
          subtitle="Verified technical skills from resume"
          icon={Layers}
          accent="blue"
          onClick={() => navigate('/resume-analyzer')}
        />
        <MetricCard
          title="Missing Required Skills"
          value={missingRequiredList.length}
          badge={missingRequiredList.length > 0 ? 'Gap Found' : 'Ready'}
          subtitle={missingRequiredList.slice(0, 3).join(', ') || 'All required skills matched'}
          icon={AlertTriangle}
          accent="rose"
          onClick={() => navigate('/skill-gaps')}
        />
        <MetricCard
          title="Learning Progress"
          value={`${displayedRoadmapPct}%`}
          badge={`${displayedRoadmapDone}/${displayedRoadmapTotal} tasks`}
          subtitle={
            liveRoadmapSummary
              ? `${liveRoadmapSummary.duration_days}d plan · ${displayedRoadmapRemaining}h remaining`
              : `${displayedRoadmapRemaining}h remaining in active roadmap`
          }
          icon={TrendingUp}
          accent="purple"
          onClick={() => navigate('/roadmap')}
        />
      </section>

      {/* Live Required vs Preferred & Matched / Missing / Additional Strip */}
      {hasLiveGap && (
        <section className="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs lg:grid-cols-3">
          <div>
            <p className="text-xs font-semibold text-emerald-700 uppercase">
              Matched Required ({latestSkillGapAnalysis.matched_required_skills.length})
            </p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {latestSkillGapAnalysis.matched_required_skills.map((s) => (
                <span
                  key={s.skill}
                  className="rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-emerald-800"
                >
                  {s.skill}
                </span>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold text-rose-700 uppercase">
              Missing Required ({latestSkillGapAnalysis.missing_required_skills.length})
            </p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {latestSkillGapAnalysis.missing_required_skills.length === 0 ? (
                <span className="text-xs text-emerald-600">No missing required skills</span>
              ) : (
                latestSkillGapAnalysis.missing_required_skills.map((s) => (
                  <span
                    key={s.skill}
                    className="rounded-md border border-rose-200 bg-rose-50 px-2.5 py-1 text-[11px] font-medium text-rose-800"
                  >
                    {s.skill} (wt {s.weight})
                  </span>
                ))
              )}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold text-purple-700 uppercase">
              Preferred &amp; Additional ({latestSkillGapAnalysis.matched_preferred_skills.length} pref ·{' '}
              {latestSkillGapAnalysis.additional_skills.length} bonus)
            </p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {latestSkillGapAnalysis.matched_preferred_skills.map((s) => (
                <span
                  key={`p-${s.skill}`}
                  className="rounded-md border border-purple-200 bg-purple-50 px-2.5 py-1 text-[11px] font-medium text-purple-800"
                >
                  ★ {s.skill}
                </span>
              ))}
              {latestSkillGapAnalysis.additional_skills.slice(0, 6).map((s) => (
                <span
                  key={`a-${s.skill}`}
                  className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-700"
                >
                  + {s.skill}
                </span>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Charts Row 1: Skills Radar + Skill Gap Bar Chart */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
          <div className="mb-4 flex items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Skills Radar vs. Target Benchmark
              </h3>
              <p className="text-xs text-slate-500">
                {hasLiveGap
                  ? `Live domain coverage for ${activeRoleTitle}`
                  : 'Proficiency across core engineering domains'}
              </p>
            </div>
            <DemoBadge mode={hasLiveGap ? 'live' : 'demo'} />
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarChartData}>
                <PolarGrid stroke="#E2E8F0" />
                <PolarAngleAxis
                  dataKey="domain"
                  tick={{ fontSize: 11, fill: '#475569' }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  tick={{ fontSize: 10, fill: '#94A3B8' }}
                />
                <Radar
                  name="Your Coverage"
                  dataKey="student"
                  stroke="#4F46E5"
                  fill="#4F46E5"
                  fillOpacity={0.28}
                />
                <Radar
                  name="Target Requirement"
                  dataKey="benchmark"
                  stroke="#94A3B8"
                  fill="#94A3B8"
                  fillOpacity={0.12}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
          <div className="mb-4 flex items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Skill Gap Breakdown by Domain
              </h3>
              <p className="text-xs text-slate-500">
                Matched vs. missing required skills for {activeRoleTitle}
              </p>
            </div>
            <Link
              to="/skill-gaps"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              Deep Dive &rarr;
            </Link>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillGapChartData} barGap={6}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                <XAxis dataKey="category" tick={{ fontSize: 11, fill: '#475569' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#475569' }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="Matched" fill="#2563EB" radius={[6, 6, 0, 0]} maxBarSize={36} />
                <Bar dataKey="Missing" fill="#F43F5E" radius={[6, 6, 0, 0]} maxBarSize={36} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Charts Row 2: Career Compatibility + Learning Progress */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
          <div className="mb-4 flex items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Career Role Compatibility
              </h3>
              <p className="text-xs text-slate-500">
                Percentage match across top engineering tracks
              </p>
            </div>
            <Link
              to="/career-prediction"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              All Roles &rarr;
            </Link>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={careerCompatibilityData}
                layout="vertical"
                margin={{ left: 10, right: 16 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: '#475569' }} />
                <YAxis
                  type="category"
                  dataKey="role"
                  width={130}
                  tick={{ fontSize: 11, fill: '#334155' }}
                />
                <Tooltip formatter={(v) => [`${v}%`, 'Compatibility']} />
                <Bar
                  dataKey="compatibility"
                  fill="#4F46E5"
                  radius={[0, 6, 6, 0]}
                  barSize={20}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
          <div className="mb-4 flex items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Learning Progress Trajectory
              </h3>
              <p className="text-xs text-slate-500">
                Weekly study hours and projected readiness trend
              </p>
            </div>
            <Link
              to="/progress"
              className="text-xs font-semibold text-purple-600 hover:text-purple-700"
            >
              Full Tracker &rarr;
            </Link>
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
                  name="Readiness Score"
                  stroke="#7C3AED"
                  fill="#7C3AED"
                  fillOpacity={0.14}
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="hours"
                  name="Study Hours"
                  stroke="#2563EB"
                  fill="#2563EB"
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Bottom Row: Recommended Roles + Recent Activity */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)] lg:col-span-7">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Recommended Career Roles
              </h3>
              <p className="text-xs text-slate-500">
                Ranked dynamically against your {userSkills.length} verified skills
              </p>
            </div>
            <Link
              to="/career-prediction"
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              <span>Compare All</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {recommendedRolesList.map((role) => (
              <div
                key={role.id}
                className="flex flex-col justify-between gap-3 rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-4 transition hover:border-indigo-200 sm:flex-row sm:items-center"
              >
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <Compass className="h-4 w-4 text-indigo-600" />
                    <span className="text-sm font-semibold text-slate-900">
                      {role.title}
                    </span>
                    <span className="rounded-md bg-white px-2 py-0.5 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">
                      {role.avgSalary}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {role.matchedCount} matched · {role.missingCount} missing
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="block text-sm font-bold text-indigo-600 tabular-nums">
                      {role.compatibility}%
                    </span>
                    <span className="block text-[10px] text-slate-500">match</span>
                  </div>
                  <Link
                    to={role.gapLink}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700"
                  >
                    Inspect Gap
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)] lg:col-span-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Recent Activity</h3>
              <p className="text-xs text-slate-500">
                {dashboardAnalytics?.recent_activity?.length
                  ? 'Live persisted account activity'
                  : 'Latest workspace actions & updates'}
              </p>
            </div>
            <Link
              to="/roadmap"
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              <Map className="h-3.5 w-3.5" />
              <span>Roadmap</span>
            </Link>
          </div>

          <div className="space-y-3.5">
            {displayedActivity.slice(0, 5).map((item) => (
              <div key={item.id} className="flex items-start gap-3">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold text-slate-900">
                    {item.title}
                  </p>
                  <p className="mt-0.5 truncate text-xs text-slate-500">{item.detail}</p>
                </div>
                <span className="shrink-0 text-[11px] text-slate-400">
                  {item.timestamp}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
