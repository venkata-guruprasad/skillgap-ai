import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Briefcase,
  CheckCircle2,
  FileText,
  GitCompare,
  GraduationCap,
  History,
  Info,
  Loader2,
  Lock,
  Plus,
  Sparkles,
  X,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
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
import EmptyState from '../components/EmptyState';
import { useApp } from '../context/AppContext';
import { ROADMAP_PLANS } from '../data/demoData';
import {
  createJobDescription,
  fetchAnalysisDetail,
  fetchAnalysisHistory,
  fetchJobs,
  fetchResumeHistory,
  runSkillGapAnalysis,
} from '../services/api';

const JOB_CATEGORIES = [
  'Data & Analytics',
  'Data & AI',
  'Software Engineering',
  'Cloud & DevOps',
  'Product & Engineering',
];

export default function SkillGapPage() {
  const {
    authToken,
    login,
    userSkills,
    roadmapHorizon,
    addCustomRoadmapTask,
    latestSkillGapAnalysis,
    setLatestSkillGapAnalysis,
    notify,
  } = useApp();

  const [searchParams, setSearchParams] = useSearchParams();

  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(() => {
    const p = searchParams.get('jobId');
    return p ? Number(p) : null;
  });
  const [selectedResumeId, setSelectedResumeId] = useState('');
  const [analysis, setAnalysis] = useState(latestSkillGapAnalysis);

  const [loadingInit, setLoadingInit] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const [authenticatingDemo, setAuthenticatingDemo] = useState(false);

  // Custom JD Paste Form state
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [customTitle, setCustomTitle] = useState('');
  const [customCompany, setCustomCompany] = useState('');
  const [customCategory, setCustomCategory] = useState('Data & AI');
  const [customRawText, setCustomRawText] = useState('');
  const [creatingJob, setCreatingJob] = useState(false);

  const loadWorkspaceData = useCallback(async () => {
    setLoadingInit(true);
    setError('');
    try {
      const jobsRes = await fetchJobs();
      const jobList = jobsRes.items || [];
      setJobs(jobList);

      const urlJobId = searchParams.get('jobId');
      if (urlJobId && jobList.some((j) => j.id === Number(urlJobId))) {
        setSelectedJobId(Number(urlJobId));
      } else if (!selectedJobId && jobList.length > 0) {
        setSelectedJobId(jobList[0].id);
      }

      if (authToken) {
        const [resHist, anaHist] = await Promise.all([
          fetchResumeHistory().catch(() => ({ items: [] })),
          fetchAnalysisHistory().catch(() => ({ items: [] })),
        ]);
        const resumeItems = resHist.items || [];
        setResumes(resumeItems);
        if (resumeItems.length > 0 && !selectedResumeId) {
          setSelectedResumeId(String(resumeItems[0].id));
        }

        const anaItems = anaHist.items || [];
        setHistory(anaItems);
        if (!analysis && anaItems.length > 0) {
          const latest = await fetchAnalysisDetail(anaItems[0].id);
          setAnalysis(latest);
          setLatestSkillGapAnalysis(latest);
        }
      }
    } catch {
      setError('Unable to load job descriptions from the backend API.');
    } finally {
      setLoadingInit(false);
    }
  }, [authToken]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    loadWorkspaceData();
  }, [authToken]); // eslint-disable-line react-hooks/exhaustive-deps

  const selectedJob = useMemo(
    () => jobs.find((j) => j.id === selectedJobId) || null,
    [jobs, selectedJobId],
  );

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

  const handleRunAnalysis = async (overrideJobId) => {
    const targetJobId = overrideJobId || selectedJobId;
    if (!authToken) {
      setError('Sign in first to run and save a live skill gap analysis.');
      return;
    }
    if (!targetJobId) {
      setError('Select a target job description first.');
      return;
    }

    setRunning(true);
    setError('');
    try {
      const payload = { job_id: targetJobId };
      if (selectedResumeId && selectedResumeId !== 'profile') {
        payload.resume_id = Number(selectedResumeId);
      } else if (userSkills.length > 0) {
        payload.candidate_skills = userSkills.map((s) => s.name);
      }

      const result = await runSkillGapAnalysis(payload);
      setAnalysis(result);
      setLatestSkillGapAnalysis(result);
      notify(`Skill gap analysis completed (${result.compatibility_score}% match)`);

      const anaHist = await fetchAnalysisHistory().catch(() => ({ items: [] }));
      setHistory(anaHist.items || []);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Failed to run skill gap analysis. Upload a resume or verify backend status.',
      );
    } finally {
      setRunning(false);
    }
  };

  const handleCreateCustomJobAndAnalyze = async (e) => {
    e.preventDefault();
    if (!authToken) {
      setError('Sign in first to save and analyze a custom job description.');
      return;
    }
    setCreatingJob(true);
    setError('');
    try {
      const created = await createJobDescription({
        title: customTitle.trim(),
        company: customCompany.trim(),
        category: customCategory,
        raw_text: customRawText.trim(),
      });
      notify(`Job description "${created.title}" analyzed & saved`);
      setCustomTitle('');
      setCustomCompany('');
      setCustomRawText('');
      setShowCustomForm(false);

      const jobsRes = await fetchJobs();
      setJobs(jobsRes.items || []);
      setSelectedJobId(created.id);
      setSearchParams({ jobId: String(created.id) });

      await handleRunAnalysis(created.id);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Invalid job description. Include role title, company, and technical requirements.',
      );
    } finally {
      setCreatingJob(false);
    }
  };

  const handleLoadHistoryItem = async (analysisId) => {
    setError('');
    try {
      const detail = await fetchAnalysisDetail(analysisId);
      setAnalysis(detail);
      setLatestSkillGapAnalysis(detail);
      if (detail.job_id) setSelectedJobId(detail.job_id);
      notify(`Loaded analysis for ${detail.job_title}`, 'info');
    } catch {
      setError('Unable to load selected analysis record.');
    }
  };

  const handleQueueSkillToRoadmap = (skillName) => {
    const activePlan = ROADMAP_PLANS[roadmapHorizon] || ROADMAP_PLANS[30];
    const firstPhaseId = activePlan.phases[0].id;
    addCustomRoadmapTask(firstPhaseId, `Master ${skillName} fundamentals & project`, 5);
  };

  const donutData = analysis
    ? [
        {
          name: 'Matched Weight',
          value: analysis.score_explanation.matched_required_weight || 0.001,
          color: '#4F46E5',
        },
        {
          name: 'Missing Weight',
          value: Math.max(
            0,
            Number(
              (
                analysis.score_explanation.total_required_weight -
                analysis.score_explanation.matched_required_weight
              ).toFixed(2),
            ),
          ),
          color: '#E2E8F0',
        },
      ]
    : [];

  const barChartData = (analysis?.category_breakdown || []).map((c) => ({
    category: c.category,
    Matched: c.matched_required,
    Missing: c.missing_required,
  }));

  const matchTypeBadge = {
    exact: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    synonym: 'bg-blue-50 text-blue-700 border-blue-200',
    semantic: 'bg-purple-50 text-purple-700 border-purple-200',
  };

  return (
    <div className="space-y-6">
      {/* Auth Notice if unauthenticated */}
      {!authToken && (
        <section className="flex flex-col justify-between gap-4 rounded-2xl border border-amber-200 bg-amber-50/80 p-5 sm:flex-row sm:items-center">
          <div className="flex items-start gap-3">
            <Lock className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            <div>
              <h2 className="text-sm font-semibold text-amber-950">
                Sign in to run live Skill Gap Analysis &amp; paste custom Job Descriptions
              </h2>
              <p className="mt-0.5 text-xs text-amber-800">
                Sample jobs are visible below. Sign in to run semantic Sentence Transformer
                matching against your uploaded resumes and persist analysis history.
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

      {/* Job Selection + Resume Source + Custom JD Trigger */}
      <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">
                Job Description Analyzer &amp; Skill Gap Engine
              </h2>
              <DemoBadge mode="live" label="Live Sentence Transformers API" />
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Select one of the 8 seeded sample jobs or paste any custom job description to
              calculate weighted required/preferred compatibility and semantic similarity.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setShowCustomForm((v) => !v)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50 px-3.5 py-2 text-xs font-semibold text-indigo-700 transition hover:bg-indigo-100"
            >
              {showCustomForm ? <X className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
              <span>{showCustomForm ? 'Close Custom JD' : 'Paste Custom Job Description'}</span>
            </button>
          </div>
        </div>

        {/* Paste Custom Job Description Form */}
        {showCustomForm && (
          <form
            onSubmit={handleCreateCustomJobAndAnalyze}
            className="mt-5 space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-indigo-950">
                Paste a Custom Job Description
              </h3>
              <span className="text-[11px] text-indigo-700">
                Extracts required, preferred &amp; soft skills, experience, education &amp;
                responsibilities
              </span>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Job Title
                </label>
                <input
                  type="text"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  placeholder="e.g., Junior Data Scientist"
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Company Name
                </label>
                <input
                  type="text"
                  value={customCompany}
                  onChange={(e) => setCustomCompany(e.target.value)}
                  placeholder="e.g., Acme AI"
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Job Category
                </label>
                <select
                  value={customCategory}
                  onChange={(e) => setCustomCategory(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                >
                  {JOB_CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700">
                Job Description Text
              </label>
              <textarea
                rows={6}
                value={customRawText}
                onChange={(e) => setCustomRawText(e.target.value)}
                placeholder={
                  'Paste Responsibilities, Required Qualifications, and Preferred Qualifications...\nExample:\nRequired Qualifications:\n- Strong proficiency in Python, SQL, Pandas, Machine Learning, NLP, and TensorFlow.\nPreferred Qualifications:\n- Experience with Docker and AWS.'
                }
                className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-3 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                required
              />
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowCustomForm(false)}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creatingJob || !authToken}
                className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {creatingJob ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Analyzing JD &amp; Running Gap...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Save JD &amp; Run Skill Gap</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-medium text-rose-700">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Resume Selector + Job Cards Grid + Run Button */}
        <div className="mt-5 grid grid-cols-1 gap-4 rounded-xl border border-slate-200/80 bg-[#F8FAFC] p-4 md:grid-cols-12 md:items-end">
          <div className="md:col-span-5">
            <label className="block text-xs font-semibold text-slate-700">
              Candidate Skill Source
            </label>
            <select
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
              className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            >
              {resumes.map((r) => (
                <option key={r.id} value={String(r.id)}>
                  Uploaded Resume: {r.file_name} ({r.technical_skill_count} verified skills)
                </option>
              ))}
              <option value="profile">
                Active Skills Profile ({userSkills.length} skills)
              </option>
            </select>
          </div>

          <div className="md:col-span-4">
            <label className="block text-xs font-semibold text-slate-700">
              Target Job Description ({jobs.length} available)
            </label>
            <select
              value={selectedJobId || ''}
              onChange={(e) => {
                const id = Number(e.target.value);
                setSelectedJobId(id);
                setSearchParams({ jobId: String(id) });
              }}
              className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            >
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} — {job.company} {job.is_sample ? '[Sample Job]' : '[Custom JD]'}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-3">
            <button
              type="button"
              onClick={() => handleRunAnalysis()}
              disabled={running || !selectedJobId || !authToken}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:opacity-50"
            >
              {running ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Computing...</span>
                </>
              ) : (
                <>
                  <GitCompare className="h-3.5 w-3.5" />
                  <span>Run Skill Gap Analysis</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Job Picker Pills */}
        {!loadingInit && jobs.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {jobs.map((job) => {
              const active = job.id === selectedJobId;
              return (
                <button
                  key={job.id}
                  type="button"
                  onClick={() => {
                    setSelectedJobId(job.id);
                    setSearchParams({ jobId: String(job.id) });
                  }}
                  className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition ${
                    active
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-800'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <span>{job.title}</span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                      job.is_sample
                        ? 'bg-slate-100 text-slate-600'
                        : 'bg-purple-100 text-purple-700'
                    }`}
                  >
                    {job.is_sample ? 'Sample' : 'Custom'}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </section>

      {/* Main Skill Gap Analysis Result */}
      {!analysis ? (
        <EmptyState
          icon={GitCompare}
          title="Run your first live Skill Gap Analysis"
          description={
            selectedJob
              ? `Click "Run Skill Gap Analysis" above to compare your verified skills against ${selectedJob.title} using Sentence Transformers semantic matching and weighted scoring.`
              : 'Select a job description or paste a custom JD above to begin.'
          }
          actionLabel={running ? 'Running...' : 'Run Skill Gap Analysis'}
          onAction={() => handleRunAnalysis()}
        />
      ) : (
        <div className="space-y-6">
          {/* Score Explanation Banner + Compatibility Donut + Domain Radar & Bar Charts */}
          <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
            <div className="flex flex-col justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-bold text-slate-950">
                    {analysis.job_title}
                  </h3>
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                      analysis.is_sample_job
                        ? 'bg-slate-100 text-slate-700'
                        : 'bg-purple-100 text-purple-700'
                    }`}
                  >
                    {analysis.is_sample_job ? 'Sample Job' : 'Custom Job Description'}
                  </span>
                  <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-[11px] font-semibold text-indigo-700">
                    {analysis.job_category}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {analysis.job_company || 'Target Employer'}
                  {analysis.resume_file_name
                    ? ` · Compared against resume: ${analysis.resume_file_name}`
                    : ' · Compared against active candidate skills'}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded-lg border border-purple-200 bg-purple-50 px-3 py-1.5 font-semibold text-purple-800">
                  JD Semantic Similarity: {analysis.jd_semantic_similarity}%
                </span>
                <span className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 font-mono text-[11px] text-slate-600">
                  {analysis.score_explanation.semantic_model}
                </span>
              </div>
            </div>

            {/* Explainable Weighted Score Formula Box */}
            <div className="mt-4 flex items-start gap-3 rounded-xl border border-indigo-100 bg-indigo-50/50 p-4">
              <Info className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
              <div className="text-xs text-indigo-950">
                <p className="font-semibold">
                  Explainable Weighted Formula:{' '}
                  <span className="font-mono font-normal">
                    {analysis.score_explanation.formula}
                  </span>
                </p>
                <p className="mt-1 text-indigo-900">
                  {analysis.score_explanation.summary_text}
                </p>
              </div>
            </div>

            {/* KPI + Charts Grid */}
            <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-12">
              {/* Overall & Preferred Score Donut */}
              <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200/80 bg-[#F8FAFC] p-5 lg:col-span-4">
                <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  Required Compatibility
                </p>
                <div className="relative mt-2 h-44 w-44">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={donutData}
                        dataKey="value"
                        innerRadius={54}
                        outerRadius={72}
                        startAngle={90}
                        endAngle={-270}
                        stroke="none"
                      >
                        {donutData.map((entry) => (
                          <Cell key={entry.name} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-extrabold text-slate-950 tabular-nums">
                      {analysis.compatibility_score}%
                    </span>
                    <span className="text-[11px] font-medium text-slate-500">
                      Weighted Fit
                    </span>
                  </div>
                </div>

                {/* Preferred Skills Calculated Separately */}
                <div className="mt-3 w-full rounded-lg border border-slate-200 bg-white p-3 text-center">
                  <p className="text-[11px] font-medium text-slate-500">
                    Preferred Skills Score (Separate)
                  </p>
                  <p className="mt-0.5 text-lg font-bold text-purple-600 tabular-nums">
                    {analysis.preferred_score !== null &&
                    analysis.preferred_score !== undefined
                      ? `${analysis.preferred_score}%`
                      : 'N/A'}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {analysis.matched_preferred_skills.length} matched ·{' '}
                    {analysis.missing_preferred_skills.length} missing
                  </p>
                </div>

                <Link
                  to="/roadmap"
                  className="mt-4 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
                >
                  <span>Close Gaps in Roadmap</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              {/* Skill Gap Bar Chart */}
              <div className="rounded-xl border border-slate-200/80 bg-white p-4 lg:col-span-4">
                <h4 className="text-xs font-semibold text-slate-900">
                  Required Skill Gap by Category
                </h4>
                <p className="text-[11px] text-slate-500">
                  Matched vs. missing required skills per domain
                </p>
                <div className="mt-3 h-56 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={barChartData} barGap={6}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                      <XAxis dataKey="category" tick={{ fontSize: 10, fill: '#475569' }} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#475569' }} />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Bar dataKey="Matched" fill="#2563EB" radius={[4, 4, 0, 0]} maxBarSize={28} />
                      <Bar dataKey="Missing" fill="#F43F5E" radius={[4, 4, 0, 0]} maxBarSize={28} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Domain Coverage Radar Chart */}
              <div className="rounded-xl border border-slate-200/80 bg-white p-4 lg:col-span-4">
                <h4 className="text-xs font-semibold text-slate-900">
                  Domain Readiness Radar
                </h4>
                <p className="text-[11px] text-slate-500">
                  Candidate coverage % vs. 100% job requirement
                </p>
                <div className="mt-3 h-56 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={analysis.radar_data || []}>
                      <PolarGrid stroke="#E2E8F0" />
                      <PolarAngleAxis
                        dataKey="domain"
                        tick={{ fontSize: 10, fill: '#475569' }}
                      />
                      <PolarRadiusAxis
                        angle={30}
                        domain={[0, 100]}
                        tick={{ fontSize: 9, fill: '#94A3B8' }}
                      />
                      <Radar
                        name="Candidate"
                        dataKey="candidate"
                        stroke="#4F46E5"
                        fill="#4F46E5"
                        fillOpacity={0.3}
                      />
                      <Radar
                        name="Required"
                        dataKey="required"
                        stroke="#94A3B8"
                        fill="#94A3B8"
                        fillOpacity={0.1}
                      />
                      <Tooltip formatter={(v) => [`${v}%`, 'Coverage']} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </section>

          {/* Required Skills Breakdown: Matched, Missing, Additional */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Matched Required Skills */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  <h3 className="text-sm font-semibold text-slate-900">
                    Matched Required Skills
                  </h3>
                </div>
                <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 tabular-nums">
                  {analysis.matched_required_skills.length}
                </span>
              </div>

              <div className="mt-4 space-y-2.5">
                {analysis.matched_required_skills.length === 0 ? (
                  <p className="text-xs text-slate-500">No required skills matched yet.</p>
                ) : (
                  analysis.matched_required_skills.map((item) => (
                    <div
                      key={item.skill}
                      className="rounded-xl border border-emerald-100 bg-emerald-50/40 px-3.5 py-2.5"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-semibold text-slate-900">
                          {item.skill}
                        </span>
                        <span
                          className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold capitalize ${
                            matchTypeBadge[item.match_type] || matchTypeBadge.exact
                          }`}
                        >
                          {item.match_type} ({Math.round(item.similarity * 100)}%)
                        </span>
                      </div>
                      <p className="mt-1 text-[11px] text-slate-500">
                        {item.category} · Weight {item.weight}
                        {item.matched_with &&
                        item.matched_with.toLowerCase() !== item.skill.toLowerCase()
                          ? ` · matched via "${item.matched_with}"`
                          : ''}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Missing Required Skills */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-rose-500" />
                  <h3 className="text-sm font-semibold text-slate-900">
                    Missing Required Skills
                  </h3>
                </div>
                <span className="rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700 tabular-nums">
                  {analysis.missing_required_skills.length}
                </span>
              </div>

              <div className="mt-4 space-y-2.5">
                {analysis.missing_required_skills.length === 0 ? (
                  <p className="text-xs text-emerald-700">
                    All required skills are covered!
                  </p>
                ) : (
                  analysis.missing_required_skills.map((item) => (
                    <div
                      key={item.skill}
                      className="flex items-center justify-between gap-2 rounded-xl border border-rose-100 bg-[#F8FAFC] px-3.5 py-2.5"
                    >
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="truncate text-xs font-semibold text-slate-900">
                            {item.skill}
                          </span>
                          <span className="rounded bg-rose-50 px-1.5 py-0.5 text-[10px] font-semibold text-rose-700">
                            Wt {item.weight}
                          </span>
                        </div>
                        <p className="mt-0.5 text-[11px] text-slate-500">
                          {item.category} · {item.priority}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleQueueSkillToRoadmap(item.skill)}
                        className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-indigo-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-indigo-600 hover:bg-indigo-50"
                      >
                        <Plus className="h-3 w-3" />
                        <span>Roadmap</span>
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Additional Candidate Skills + Separate Preferred Breakdown */}
            <div className="space-y-5">
              <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-purple-600" />
                    <h3 className="text-sm font-semibold text-slate-900">
                      Preferred Skills Breakdown
                    </h3>
                  </div>
                  <span className="text-xs font-bold text-purple-700 tabular-nums">
                    {analysis.preferred_score !== null &&
                    analysis.preferred_score !== undefined
                      ? `${analysis.preferred_score}%`
                      : 'None'}
                  </span>
                </div>

                <div className="mt-3 space-y-2">
                  {analysis.matched_preferred_skills.length === 0 &&
                  analysis.missing_preferred_skills.length === 0 ? (
                    <p className="text-xs text-slate-500">
                      No separate preferred skills listed for this job.
                    </p>
                  ) : (
                    <div className="flex flex-wrap gap-1.5">
                      {analysis.matched_preferred_skills.map((s) => (
                        <span
                          key={s.skill}
                          className="rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-emerald-700"
                        >
                          ✓ {s.skill}
                        </span>
                      ))}
                      {analysis.missing_preferred_skills.map((s) => (
                        <span
                          key={s.skill}
                          className="rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1 text-[11px] font-medium text-amber-800"
                        >
                          + {s.skill} (Preferred)
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <h3 className="text-sm font-semibold text-slate-900">
                    Additional Candidate Skills
                  </h3>
                  <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 tabular-nums">
                    {analysis.additional_skills.length}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {analysis.additional_skills.length === 0 ? (
                    <p className="text-xs text-slate-500">
                      All candidate skills were directly relevant to this role.
                    </p>
                  ) : (
                    analysis.additional_skills.map((s) => (
                      <span
                        key={s.skill}
                        className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-700"
                      >
                        {s.skill}
                      </span>
                    ))
                  )}
                </div>
              </div>
            </div>
          </section>

          {/* Extracted Job Details (Experience, Education, Responsibilities, Soft Skills) */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <Briefcase className="h-4 w-4 text-indigo-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Key Responsibilities
                </h3>
              </div>
              <ul className="mt-3 list-disc space-y-1.5 pl-4 text-xs text-slate-600">
                {(analysis.job_details?.responsibilities || []).length === 0 ? (
                  <li className="list-none -ml-4 text-slate-400">
                    No separate responsibilities section extracted.
                  </li>
                ) : (
                  analysis.job_details.responsibilities.map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))
                )}
              </ul>
            </div>

            <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <GraduationCap className="h-4 w-4 text-blue-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Experience &amp; Education
                </h3>
              </div>
              <div className="mt-3 space-y-3 text-xs text-slate-600">
                <div>
                  <p className="font-semibold text-slate-800">Experience Requirements</p>
                  <ul className="mt-1 space-y-1">
                    {(analysis.job_details?.experience_requirements || []).map((e, i) => (
                      <li key={i} className="rounded bg-slate-50 px-2.5 py-1.5">
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-semibold text-slate-800">Education Requirements</p>
                  <ul className="mt-1 space-y-1">
                    {(analysis.job_details?.education_requirements || []).map((e, i) => (
                      <li key={i} className="rounded bg-slate-50 px-2.5 py-1.5">
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <FileText className="h-4 w-4 text-purple-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Soft Skills Mentioned in JD
                </h3>
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {(analysis.job_details?.soft_skills || []).length === 0 ? (
                  <p className="text-xs text-slate-400">No soft skills explicitly listed.</p>
                ) : (
                  analysis.job_details.soft_skills.map((s) => (
                    <span
                      key={s.name}
                      className="rounded-md border border-purple-200 bg-purple-50 px-2.5 py-1 text-xs font-medium text-purple-800"
                    >
                      {s.name}
                    </span>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>
      )}

      {/* Analysis History */}
      {authToken && history.length > 0 && (
        <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-indigo-600" />
            <h3 className="text-sm font-semibold text-slate-900">
              Recent Skill Gap Analyses ({history.length})
            </h3>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-2.5 md:grid-cols-2 lg:grid-cols-3">
            {history.slice(0, 6).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleLoadHistoryItem(item.id)}
                className={`flex items-center justify-between rounded-xl border p-3 text-left transition ${
                  analysis?.id === item.id
                    ? 'border-indigo-400 bg-indigo-50/60'
                    : 'border-slate-200 bg-[#F8FAFC] hover:border-slate-300'
                }`}
              >
                <div className="min-w-0">
                  <p className="truncate text-xs font-semibold text-slate-900">
                    {item.job_title}
                  </p>
                  <p className="mt-0.5 truncate text-[11px] text-slate-500">
                    {item.matched_required_count} matched · {item.missing_required_count} missing
                  </p>
                </div>
                <span className="ml-2 shrink-0 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-bold text-indigo-700 tabular-nums">
                  {item.compatibility_score}%
                </span>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
