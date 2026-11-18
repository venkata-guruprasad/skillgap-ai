import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  ArrowRight,
  Bookmark,
  BookmarkCheck,
  Briefcase,
  Building2,
  CheckCircle2,
  DollarSign,
  Filter,
  GitCompare,
  Loader2,
  MapPin,
  Plus,
  Search,
  X,
} from 'lucide-react';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import { useApp } from '../context/AppContext';
import { computeSkillComparison } from '../data/demoData';
import { fetchJobDetail, fetchJobs } from '../services/api';

export default function JobExplorerPage() {
  const { authToken, userSkills, savedJobIds, appliedJobIds, toggleSaveJob, applyToJob } =
    useApp();
  const [searchParams, setSearchParams] = useSearchParams();

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [workMode, setWorkMode] = useState('All');
  const [minMatch, setMinMatch] = useState(0);
  const [savedOnly, setSavedOnly] = useState(false);
  const [activeJobDetail, setActiveJobDetail] = useState(null);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q !== null) setQuery(q);
  }, [searchParams]);

  useEffect(() => {
    setLoading(true);
    fetchJobs()
      .then((res) => setJobs(res.items || []))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, [authToken]);

  const categories = useMemo(
    () => ['All', ...Array.from(new Set(jobs.map((j) => j.category)))],
    [jobs],
  );

  const enrichedJobs = useMemo(() => {
    return jobs
      .map((job) => {
        const reqNames = (job.required_skills || []).map((s) => s.name);
        const cmp = computeSkillComparison(userSkills, reqNames);
        return {
          ...job,
          idKey: `db-job-${job.id}`,
          compatibility: cmp.score,
          matchedNames: new Set(cmp.matched.map((m) => m.name.toLowerCase())),
        };
      })
      .sort((a, b) => b.compatibility - a.compatibility);
  }, [jobs, userSkills]);

  const filteredJobs = useMemo(() => {
    const q = query.trim().toLowerCase();
    return enrichedJobs.filter((job) => {
      if (categoryFilter !== 'All' && job.category !== categoryFilter) return false;
      if (workMode !== 'All' && (job.work_mode || '') !== workMode) return false;
      if (job.compatibility < minMatch) return false;
      if (savedOnly && !savedJobIds.includes(job.idKey)) return false;
      if (!q) return true;
      const hay = `${job.title} ${job.company || ''} ${job.category} ${job.location || ''} ${(job.required_skills || []).map((s) => s.name).join(' ')}`.toLowerCase();
      return hay.includes(q);
    });
  }, [enrichedJobs, query, categoryFilter, workMode, minMatch, savedOnly, savedJobIds]);

  const resetFilters = () => {
    setQuery('');
    setCategoryFilter('All');
    setWorkMode('All');
    setMinMatch(0);
    setSavedOnly(false);
    setSearchParams({});
  };

  const handleOpenDetail = async (job) => {
    try {
      const detail = await fetchJobDetail(job.id);
      setActiveJobDetail({ ...detail, compatibility: job.compatibility, matchedNames: job.matchedNames });
    } catch {
      setActiveJobDetail(null);
    }
  };

  const hasActiveFilters =
    query.trim() !== '' ||
    categoryFilter !== 'All' ||
    workMode !== 'All' ||
    minMatch > 0 ||
    savedOnly;

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-sm font-semibold text-slate-900">
              Job Explorer &amp; Seeded Sample Descriptions
            </h2>
            <DemoBadge mode="live" label="Live GET /api/jobs" />
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">
              Showing <span className="font-semibold text-slate-900">{filteredJobs.length}</span>{' '}
              of {enrichedJobs.length} roles
            </span>
            <Link
              to="/skill-gaps"
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Paste Custom JD</span>
            </Link>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-12">
          <div className="relative md:col-span-5">
            <Search className="pointer-events-none absolute top-1/2 left-3.5 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by job title, company, or required skill (e.g., Python, SQL)"
              className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pr-9 pl-10 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="absolute top-1/2 right-2.5 -translate-y-1/2 rounded p-1 text-slate-400 hover:text-slate-600"
                aria-label="Clear search"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Filter by category"
            className="rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-xs font-medium text-slate-700 focus:border-indigo-500 focus:outline-none md:col-span-3"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === 'All' ? 'All Categories' : c}
              </option>
            ))}
          </select>

          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            aria-label="Filter by work mode"
            className="rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-xs font-medium text-slate-700 focus:border-indigo-500 focus:outline-none md:col-span-2"
          >
            <option value="All">All Modes</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
          </select>

          <select
            value={minMatch}
            onChange={(e) => setMinMatch(Number(e.target.value))}
            aria-label="Filter by minimum compatibility"
            className="rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-xs font-medium text-slate-700 focus:border-indigo-500 focus:outline-none md:col-span-2"
          >
            <option value={0}>Any Match</option>
            <option value={50}>50%+ Match</option>
            <option value={70}>70%+ Match</option>
          </select>
        </div>

        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 pt-1">
          <button
            type="button"
            onClick={() => setSavedOnly((v) => !v)}
            className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition ${
              savedOnly
                ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
                : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Bookmark className="h-3.5 w-3.5" />
            <span>Saved Jobs Only</span>
          </button>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={resetFilters}
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              <Filter className="h-3.5 w-3.5" />
              <span>Reset all filters</span>
            </button>
          )}
        </div>
      </section>

      {loading ? (
        <div className="flex items-center justify-center rounded-2xl border border-slate-200 bg-white py-14 text-xs text-slate-500">
          <Loader2 className="mr-2 h-4 w-4 animate-spin text-indigo-600" />
          Loading job descriptions from backend...
        </div>
      ) : filteredJobs.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No matching jobs found"
          description="Try broadening your search keywords or resetting filters."
          actionLabel="Reset Filters"
          onAction={resetFilters}
        />
      ) : (
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {filteredJobs.map((job) => {
            const isSaved = savedJobIds.includes(job.idKey);
            const isApplied = appliedJobIds.includes(job.idKey);
            const matchTone =
              job.compatibility >= 75
                ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                : job.compatibility >= 50
                ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                : 'border-amber-200 bg-amber-50 text-amber-700';

            return (
              <article
                key={job.id}
                className="flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs transition hover:border-indigo-200 hover:shadow-md"
              >
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        <span
                          className={`rounded px-2 py-0.5 text-[10px] font-semibold ${
                            job.is_sample
                              ? 'bg-slate-100 text-slate-700'
                              : 'bg-purple-100 text-purple-700'
                          }`}
                        >
                          {job.is_sample ? 'Sample Job' : 'Custom JD'}
                        </span>
                        <span className="inline-flex items-center gap-1 font-medium text-slate-700">
                          <Building2 className="h-3.5 w-3.5 text-slate-400" />
                          {job.company || 'Employer'}
                        </span>
                        <span>·</span>
                        <span>{job.category}</span>
                      </div>
                      <h3 className="mt-1.5 text-base font-bold text-slate-950">
                        {job.title}
                      </h3>
                    </div>

                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full border px-2.5 py-1 text-xs font-bold tabular-nums ${matchTone}`}
                      >
                        {job.compatibility}% est.
                      </span>
                      <button
                        type="button"
                        onClick={() =>
                          toggleSaveJob({
                            id: job.idKey,
                            title: job.title,
                            company: job.company,
                            location: job.location || 'Remote',
                          })
                        }
                        aria-label={isSaved ? 'Remove bookmark' : 'Save job'}
                        className={`rounded-lg border p-1.5 transition ${
                          isSaved
                            ? 'border-indigo-200 bg-indigo-50 text-indigo-600'
                            : 'border-slate-200 text-slate-400 hover:bg-slate-50 hover:text-slate-700'
                        }`}
                      >
                        {isSaved ? (
                          <BookmarkCheck className="h-4 w-4" />
                        ) : (
                          <Bookmark className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                    {job.location && (
                      <span className="inline-flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-slate-400" />
                        {job.location}
                      </span>
                    )}
                    {job.salary_range && (
                      <span className="inline-flex items-center gap-1">
                        <DollarSign className="h-3.5 w-3.5 text-slate-400" />
                        {job.salary_range}
                      </span>
                    )}
                    {job.experience_level && <span>{job.experience_level} Level</span>}
                  </div>

                  {/* Required Skills */}
                  <div className="mt-4">
                    <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                      Required Skills ({job.required_skill_count})
                    </p>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {(job.required_skills || []).map((skill) => {
                        const matched = job.matchedNames.has(skill.name.toLowerCase());
                        return (
                          <span
                            key={skill.name}
                            className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium ${
                              matched
                                ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                                : 'border-slate-200 bg-slate-50 text-slate-600'
                            }`}
                          >
                            {matched && <CheckCircle2 className="h-3 w-3" />}
                            {skill.name}
                          </span>
                        );
                      })}
                    </div>
                  </div>

                  {job.preferred_skill_count > 0 && (
                    <div className="mt-3">
                      <p className="text-[10px] font-semibold tracking-wide text-slate-400 uppercase">
                        Preferred ({job.preferred_skill_count}):{' '}
                        <span className="font-normal text-slate-600">
                          {(job.preferred_skills || []).map((s) => s.name).join(', ')}
                        </span>
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-4">
                  <Link
                    to={`/skill-gaps?jobId=${job.id}`}
                    className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700"
                  >
                    <GitCompare className="h-3.5 w-3.5" />
                    <span>Analyze Skill Gap</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                  <button
                    type="button"
                    onClick={() => handleOpenDetail(job)}
                    className="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Details
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      applyToJob({
                        id: job.idKey,
                        title: job.title,
                        company: job.company || 'Employer',
                      })
                    }
                    disabled={isApplied}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:border-emerald-200 disabled:bg-emerald-50 disabled:text-emerald-700"
                  >
                    {isApplied ? 'Tracked' : 'Track'}
                  </button>
                </div>
              </article>
            );
          })}
        </section>
      )}

      {/* Job Details Modal */}
      {activeJobDetail && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[1px]"
          onClick={() => setActiveJobDetail(null)}
        >
          <div
            className="max-h-[85vh] w-full max-w-xl overflow-y-auto rounded-2xl border border-slate-200 bg-white p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold text-indigo-600">
                  {activeJobDetail.company} · {activeJobDetail.category}{' '}
                  {activeJobDetail.is_sample ? '(Sample Job)' : '(Custom JD)'}
                </p>
                <h3 className="mt-1 text-lg font-bold text-slate-950">
                  {activeJobDetail.title}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setActiveJobDetail(null)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100"
                aria-label="Close modal"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs">
              <div>
                <p className="font-semibold text-slate-800">Responsibilities</p>
                <ul className="mt-1 list-disc space-y-1 pl-4 text-slate-600">
                  {(activeJobDetail.extracted?.responsibilities || []).map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="font-semibold text-slate-800">Experience &amp; Education</p>
                <ul className="mt-1 space-y-1 text-slate-600">
                  {[
                    ...(activeJobDetail.extracted?.experience_requirements || []),
                    ...(activeJobDetail.extracted?.education_requirements || []),
                  ].map((line, i) => (
                    <li key={i} className="rounded bg-slate-50 px-2.5 py-1.5">
                      {line}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2 border-t border-slate-100 pt-4">
              <button
                type="button"
                onClick={() => setActiveJobDetail(null)}
                className="rounded-lg border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Close
              </button>
              <Link
                to={`/skill-gaps?jobId=${activeJobDetail.id}`}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
              >
                Run Full Skill Gap Analysis
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
