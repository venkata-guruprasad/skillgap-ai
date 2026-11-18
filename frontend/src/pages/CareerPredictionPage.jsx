import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Compass,
  Cpu,
  DollarSign,
  GitCompare,
  Info,
  Loader2,
  Lock,
  Map,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import { useApp } from '../context/AppContext';
import {
  fetchCareerRecommendations,
  fetchResumeHistory,
  predictCareerRoles,
} from '../services/api';

const INTEREST_OPTIONS = [
  { key: 'AI', label: 'AI & NLP' },
  { key: 'ML', label: 'Machine Learning' },
  { key: 'Data', label: 'Data & Analytics' },
  { key: 'Fullstack', label: 'Full Stack Web' },
  { key: 'Backend', label: 'Backend & APIs' },
  { key: 'Frontend', label: 'Frontend & UI' },
  { key: 'Cloud', label: 'Cloud & DevOps' },
  { key: 'Cybersecurity', label: 'Cybersecurity' },
  { key: 'Business', label: 'Business Strategy' },
];

export default function CareerPredictionPage() {
  const {
    authToken,
    login,
    userSkills,
    notify,
  } = useApp();
  const navigate = useNavigate();

  const [resumes, setResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState('');
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [prediction, setPrediction] = useState(null);

  const [loadingInit, setLoadingInit] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [authenticatingDemo, setAuthenticatingDemo] = useState(false);
  const [showModelDetails, setShowModelDetails] = useState(false);
  const [error, setError] = useState('');

  const loadInitialData = useCallback(async () => {
    if (!authToken) {
      setLoadingInit(false);
      return;
    }
    setLoadingInit(true);
    setError('');
    try {
      const resHist = await fetchResumeHistory().catch(() => ({ items: [] }));
      const items = resHist.items || [];
      setResumes(items);
      if (items.length > 0 && !selectedResumeId) {
        setSelectedResumeId(String(items[0].id));
      }

      try {
        const latest = await fetchCareerRecommendations();
        setPrediction(latest);
        if (latest.input_summary?.career_interests?.length) {
          setSelectedInterests(latest.input_summary.career_interests);
        }
      } catch (err) {
        if (err?.response?.status !== 404) {
          setError('Unable to load saved career recommendations.');
        }
      }
    } finally {
      setLoadingInit(false);
    }
  }, [authToken]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    loadInitialData();
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

  const toggleInterest = (key) => {
    setSelectedInterests((prev) =>
      prev.includes(key) ? prev.filter((item) => item !== key) : [...prev, key],
    );
  };

  const handleRunPrediction = async () => {
    if (!authToken) {
      setError('Sign in first to run live ML career prediction.');
      return;
    }
    setPredicting(true);
    setError('');
    try {
      const payload = {
        career_interests: selectedInterests,
      };
      if (selectedResumeId && selectedResumeId !== 'profile') {
        payload.resume_id = Number(selectedResumeId);
      } else {
        payload.resume_skills = userSkills.map((s) => s.name);
      }

      const result = await predictCareerRoles(payload);
      setPrediction(result);
      notify(
        `Top match: ${result.top_recommendations[0]?.career_title} (${result.top_recommendations[0]?.compatibility_score}%)`,
      );
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Failed to generate ML career predictions. Upload a resume or check backend status.',
      );
    } finally {
      setPredicting(false);
    }
  };

  const handleGenerateRoadmapForRole = (rec) => {
    notify(`Opening AI Learning Roadmap for ${rec.career_title}`);
    navigate(`/roadmap?role=${encodeURIComponent(rec.career_title)}`);
  };

  const recommendations = prediction?.top_recommendations || [];
  const evalSummary = prediction?.model_metadata?.evaluation_summary || null;

  const chartData = recommendations.map((r) => ({
    name: r.career_title.replace(' Engineer', ' Eng.').replace(' Developer', ' Dev.'),
    Compatibility: r.compatibility_score,
    SkillGap: r.score_breakdown.skill_gap_score,
    Semantic: r.score_breakdown.semantic_similarity,
  }));

  return (
    <div className="space-y-6">
      {/* Auth Gate Notice */}
      {!authToken && (
        <section className="flex flex-col justify-between gap-4 rounded-2xl border border-amber-200 bg-amber-50/80 p-5 sm:flex-row sm:items-center">
          <div className="flex items-start gap-3">
            <Lock className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            <div>
              <h2 className="text-sm font-semibold text-amber-950">
                Sign in to run live ML Career Predictions
              </h2>
              <p className="mt-0.5 text-xs text-amber-800">
                Our 12-role Scikit-learn + Sentence Transformers + Skill Gap engine runs on
                your authenticated resume and skill profile.
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

      {/* Prediction Controls Card */}
      <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">
                ML Career Prediction Engine (12 Roles)
              </h2>
              <DemoBadge mode="live" label="Live TF-IDF + MiniLM + Skill Gap" />
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Combines a trained Scikit-learn classifier, Sentence Transformers cosine
              similarity, and the weighted Skill Gap Engine to rank your top 5 career paths.
            </p>
          </div>

          {evalSummary && (
            <button
              type="button"
              onClick={() => setShowModelDetails((v) => !v)}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              <Cpu className="h-3.5 w-3.5 text-indigo-600" />
              <span>Model Evaluation Metrics</span>
              {showModelDetails ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
            </button>
          )}
        </div>

        {/* Source Selector + Career Interests Chips + Predict CTA */}
        <div className="mt-5 space-y-4 rounded-xl border border-slate-200/80 bg-[#F8FAFC] p-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-12 md:items-end">
            <div className="md:col-span-8">
              <label className="block text-xs font-semibold text-slate-700">
                Candidate Profile Source
              </label>
              <select
                value={selectedResumeId}
                onChange={(e) => setSelectedResumeId(e.target.value)}
                className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
              >
                {resumes.map((r) => (
                  <option key={r.id} value={String(r.id)}>
                    Uploaded Resume: {r.file_name} ({r.technical_skill_count} extracted skills)
                  </option>
                ))}
                <option value="profile">
                  Active Skills Profile ({userSkills.length} skills)
                </option>
              </select>
            </div>

            <div className="md:col-span-4">
              <button
                type="button"
                onClick={handleRunPrediction}
                disabled={predicting || !authToken}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:opacity-50"
              >
                {predicting ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Running ML Model...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Predict Top 5 Careers</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold text-slate-700">
              Preferred Career Interests (Optional)
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {INTEREST_OPTIONS.map((opt) => {
                const active = selectedInterests.includes(opt.key);
                return (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => toggleInterest(opt.key)}
                    className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                      active
                        ? 'border-indigo-500 bg-indigo-600 text-white'
                        : 'border-slate-300 bg-white text-slate-700 hover:border-indigo-300'
                    }`}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Expandable Model Evaluation Transparency Panel */}
        {showModelDetails && evalSummary && (
          <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-semibold text-slate-900">
                Classifier: {prediction.model_metadata.selected_classifier} · Semantic:{' '}
                {prediction.model_metadata.semantic_model}
              </p>
              <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[11px] font-semibold text-amber-800">
                Synthetic Benchmark Dataset ({evalSummary.train_samples} train /{' '}
                {evalSummary.test_samples} held-out test)
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-lg bg-white p-3 ring-1 ring-slate-200">
                <p className="text-[11px] text-slate-500">Test Accuracy</p>
                <p className="mt-0.5 text-base font-bold text-slate-900 tabular-nums">
                  {(evalSummary.accuracy * 100).toFixed(1)}%
                </p>
              </div>
              <div className="rounded-lg bg-white p-3 ring-1 ring-slate-200">
                <p className="text-[11px] text-slate-500">Macro Precision</p>
                <p className="mt-0.5 text-base font-bold text-slate-900 tabular-nums">
                  {(evalSummary.precision_macro * 100).toFixed(1)}%
                </p>
              </div>
              <div className="rounded-lg bg-white p-3 ring-1 ring-slate-200">
                <p className="text-[11px] text-slate-500">Macro Recall</p>
                <p className="mt-0.5 text-base font-bold text-slate-900 tabular-nums">
                  {(evalSummary.recall_macro * 100).toFixed(1)}%
                </p>
              </div>
              <div className="rounded-lg bg-white p-3 ring-1 ring-slate-200">
                <p className="text-[11px] text-slate-500">Macro F1-Score</p>
                <p className="mt-0.5 text-base font-bold text-indigo-600 tabular-nums">
                  {(evalSummary.f1_macro * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            <p className="mt-3 text-[11px] text-slate-600">
              {evalSummary.evaluation_notice}
            </p>
          </div>
        )}

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-medium text-rose-700">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </section>

      {/* Recommendations Results or Empty State */}
      {loadingInit ? (
        <div className="flex items-center justify-center rounded-2xl border border-slate-200 bg-white py-14 text-xs text-slate-500">
          <Loader2 className="mr-2 h-4 w-4 animate-spin text-indigo-600" />
          Loading your ML career recommendations...
        </div>
      ) : recommendations.length === 0 ? (
        <EmptyState
          icon={Compass}
          title="No ML career predictions yet"
          description="Select your uploaded resume or active skills profile above and click 'Predict Top 5 Careers' to evaluate all 12 supported career tracks."
          actionLabel={predicting ? 'Predicting...' : 'Predict Top 5 Careers'}
          onAction={handleRunPrediction}
        />
      ) : (
        <div className="space-y-6">
          {/* Disclaimer + Top-5 Chart */}
          <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
            <div className="flex items-start gap-2.5 rounded-xl border border-indigo-100 bg-indigo-50/50 p-3.5 text-xs text-indigo-950">
              <Info className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
              <span>{prediction.disclaimer}</span>
            </div>

            <div className="mt-5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-indigo-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Top 5 Recommended Career Roles (out of {prediction.total_roles_evaluated}{' '}
                  evaluated)
                </h3>
              </div>
              {prediction.resume_file_name && (
                <span className="text-xs text-slate-500">
                  Source: {prediction.resume_file_name}
                </span>
              )}
            </div>

            <div className="mt-4 h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#475569' }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#475569' }} />
                  <Tooltip formatter={(val) => [`${val}%`]} />
                  <Bar
                    dataKey="Compatibility"
                    name="Compatibility Score"
                    fill="#4F46E5"
                    radius={[6, 6, 0, 0]}
                    maxBarSize={42}
                  />
                  <Bar
                    dataKey="SkillGap"
                    name="Skill Gap Match"
                    fill="#2563EB"
                    radius={[6, 6, 0, 0]}
                    maxBarSize={42}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Top 5 Career Recommendation Cards */}
          <section className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {recommendations.map((rec, idx) => (
              <article
                key={rec.career_title}
                className={`flex flex-col justify-between rounded-2xl border bg-white p-6 shadow-xs transition hover:shadow-md ${
                  idx === 0
                    ? 'border-indigo-400 ring-1 ring-indigo-500/20 lg:col-span-2'
                    : 'border-slate-200/80'
                }`}
              >
                <div>
                  {/* Header */}
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                            idx === 0
                              ? 'bg-indigo-600 text-white'
                              : 'bg-indigo-50 text-indigo-700'
                          }`}
                        >
                          #{idx + 1} {idx === 0 ? 'Top Recommendation' : 'Match'}
                        </span>
                        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-700">
                          {rec.category}
                        </span>
                        <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                          <DollarSign className="h-3.5 w-3.5" />
                          {rec.avg_salary}
                        </span>
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-600">
                          <TrendingUp className="h-3.5 w-3.5" />
                          {rec.demand_level} Demand
                        </span>
                      </div>
                      <h3 className="mt-2 flex items-center gap-2 text-lg font-bold text-slate-950">
                        <Compass className="h-5 w-5 text-indigo-600" />
                        <span>{rec.career_title}</span>
                      </h3>
                    </div>

                    <div className="shrink-0 rounded-xl border border-indigo-100 bg-indigo-50 px-3.5 py-2 text-center">
                      <span className="block text-xl font-extrabold text-indigo-700 tabular-nums">
                        {rec.compatibility_score}%
                      </span>
                      <span className="block text-[10px] font-semibold text-indigo-500 uppercase">
                        Compatibility
                      </span>
                    </div>
                  </div>

                  {/* Progress Bar & Transparent ML Sub-Scores */}
                  <div className="mt-4">
                    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-indigo-600 transition-all duration-300"
                        style={{ width: `${rec.compatibility_score}%` }}
                      />
                    </div>
                    <div className="mt-2.5 flex flex-wrap gap-2 text-[11px] text-slate-600">
                      <span className="rounded bg-slate-100 px-2 py-0.5 font-medium">
                        Skill Gap: {rec.score_breakdown.skill_gap_score}%
                      </span>
                      <span className="rounded bg-blue-50 px-2 py-0.5 font-medium text-blue-700">
                        ML Classifier: {rec.score_breakdown.ml_classifier_score}%
                      </span>
                      <span className="rounded bg-purple-50 px-2 py-0.5 font-medium text-purple-700">
                        MiniLM Semantic: {rec.score_breakdown.semantic_similarity}%
                      </span>
                      {rec.score_breakdown.interest_bonus > 0 && (
                        <span className="rounded bg-emerald-50 px-2 py-0.5 font-medium text-emerald-700">
                          Interest Boost: +{rec.score_breakdown.interest_bonus}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Explanation */}
                  <div className="mt-4 rounded-xl border border-slate-100 bg-[#F8FAFC] p-3.5">
                    <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                      Recommendation Explanation
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-slate-700">
                      {rec.explanation}
                    </p>
                  </div>

                  {/* Skills Grid */}
                  <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <p className="text-xs font-semibold text-slate-700">
                        Skills Matched ({rec.matching_skills.length})
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {rec.matching_skills.length === 0 ? (
                          <span className="text-xs text-slate-400">None yet</span>
                        ) : (
                          rec.matching_skills.map((skill) => (
                            <span
                              key={skill}
                              className="inline-flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700"
                            >
                              <CheckCircle2 className="h-3 w-3" />
                              {skill}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-semibold text-slate-700">
                        Missing Skills ({rec.missing_skills.length})
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {rec.missing_skills.length === 0 ? (
                          <span className="text-xs text-emerald-600">
                            All required skills matched!
                          </span>
                        ) : (
                          rec.missing_skills.map((skill) => (
                            <span
                              key={skill}
                              className="rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-[11px] font-medium text-rose-700"
                            >
                              {skill}
                            </span>
                          ))
                        )}
                      </div>
                    </div>
                  </div>

                  {rec.required_additional_skills?.length > 0 && (
                    <div className="mt-3 border-t border-slate-100 pt-3 text-[11px] text-slate-500">
                      <span className="font-semibold text-slate-700">
                        Required additional skills to prioritize:{' '}
                      </span>
                      {rec.required_additional_skills.join(', ')}
                    </div>
                  )}
                </div>

                {/* Action Buttons: View Skill Gaps + Generate Roadmap */}
                <div className="mt-5 flex flex-wrap items-center gap-2.5 border-t border-slate-100 pt-4">
                  <Link
                    to={
                      rec.linked_job_id
                        ? `/skill-gaps?jobId=${rec.linked_job_id}`
                        : '/skill-gaps'
                    }
                    className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700"
                  >
                    <GitCompare className="h-3.5 w-3.5" />
                    <span>View Skill Gaps</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                  <button
                    type="button"
                    onClick={() => handleGenerateRoadmapForRole(rec)}
                    className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700"
                  >
                    <Map className="h-3.5 w-3.5" />
                    <span>Generate Roadmap</span>
                  </button>
                </div>
              </article>
            ))}
          </section>
        </div>
      )}
    </div>
  );
}
