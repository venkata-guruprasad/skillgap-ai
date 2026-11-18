import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Award,
  Briefcase,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Download,
  FileCheck2,
  FileText,
  FolderGit2,
  GraduationCap,
  History,
  Loader2,
  Lock,
  ShieldCheck,
  Sparkles,
  Trash2,
  UploadCloud,
} from 'lucide-react';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import { useApp } from '../context/AppContext';
import {
  deleteResumeById,
  extractSkillsFromText,
  fetchResumeDetail,
  fetchResumeHistory,
  uploadResumeFile,
} from '../services/api';

const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB
const ALLOWED_EXTENSIONS = ['.pdf', '.docx'];

function buildMarkdownReport(detail) {
  const { analysis } = detail;
  const lines = [
    `# SkillGap AI – Resume Analysis Report`,
    ``,
    `- **File Name**: ${detail.file_name}`,
    `- **File Type**: ${detail.file_type}`,
    `- **Extraction Status**: ${detail.extraction_status}`,
    `- **ATS Structure Score**: ${analysis.summary.ats_score}/100`,
    `- **Word Count**: ${analysis.summary.word_count}`,
    `- **Analyzed At**: ${new Date(detail.created_at).toLocaleString()}`,
    ``,
    `## Technical Skills (${analysis.technical_skills.length})`,
    ...analysis.technical_skills.map(
      (s) =>
        `- **${s.name}** (${s.category}) — ${Math.round(s.confidence * 100)}% confidence${
          s.evidence?.[0] ? ` | Evidence: "${s.evidence[0]}"` : ''
        }`,
    ),
    ``,
    `## Soft Skills (${analysis.soft_skills.length})`,
    ...(analysis.soft_skills.length
      ? analysis.soft_skills.map((s) => `- **${s.name}** (${Math.round(s.confidence * 100)}%)`)
      : ['- None explicitly detected']),
    ``,
    `## Education (${analysis.education.length})`,
    ...(analysis.education.length
      ? analysis.education.map(
          (e) => `- **${e.degree}**${e.institution ? ` — ${e.institution}` : ''}${e.period ? ` (${e.period})` : ''}`,
        )
      : ['- No education section detected']),
    ``,
    `## Work Experience (${analysis.experience.length})`,
    ...(analysis.experience.length
      ? analysis.experience.flatMap((exp) => [
          `- **${exp.role}**${exp.organization ? ` | ${exp.organization}` : ''}${exp.duration ? ` (${exp.duration})` : ''}`,
          ...(exp.highlights || []).map((h) => `  - ${h}`),
        ])
      : ['- No work experience section detected']),
    ``,
    `## Projects (${analysis.projects.length})`,
    ...(analysis.projects.length
      ? analysis.projects.map(
          (p) =>
            `- **${p.title}**: ${p.description}${
              p.technologies?.length ? ` [Tech: ${p.technologies.join(', ')}]` : ''
            }`,
        )
      : ['- No projects section detected']),
    ``,
    `## Certifications (${analysis.certifications.length})`,
    ...(analysis.certifications.length
      ? analysis.certifications.map((c) => `- ${c}`)
      : ['- None detected']),
    ``,
    `## Recommendations`,
    ...(analysis.summary.recommendations || []).map((r) => `- ${r}`),
  ];
  return lines.join('\n');
}

function triggerFileDownload(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function ResumeAnalyzerPage() {
  const { authToken, login, activeResumeDetail, syncLiveResumeAnalysis, clearResume, notify } =
    useApp();

  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [duplicateInfo, setDuplicateInfo] = useState(null);

  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [currentDetail, setCurrentDetail] = useState(activeResumeDetail);
  const [expandedEvidence, setExpandedEvidence] = useState({});

  // Quick Skill Extractor (POST /api/skills/extract)
  const [showTextExtractor, setShowTextExtractor] = useState(false);
  const [rawSnippet, setRawSnippet] = useState('');
  const [snippetResult, setSnippetResult] = useState(null);
  const [extractingSnippet, setExtractingSnippet] = useState(false);
  const [authenticatingDemo, setAuthenticatingDemo] = useState(false);

  const loadHistory = useCallback(async () => {
    if (!authToken) return;
    setLoadingHistory(true);
    try {
      const data = await fetchResumeHistory();
      setHistory(data.items || []);
      if (!currentDetail && data.items?.length > 0) {
        const latest = await fetchResumeDetail(data.items[0].id);
        setCurrentDetail(latest);
        syncLiveResumeAnalysis(latest);
      }
    } catch {
      // Keep UI graceful if backend is temporarily unreachable
    } finally {
      setLoadingHistory(false);
    }
  }, [authToken, currentDetail, syncLiveResumeAnalysis]);

  useEffect(() => {
    loadHistory();
  }, [authToken]); // eslint-disable-line react-hooks/exhaustive-deps

  const validateAndSelectFile = (file) => {
    if (!file) return;
    setError('');
    setDuplicateInfo(null);
    const lowerName = file.name.toLowerCase();
    const validExt = ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
    if (!validExt) {
      setError('Unsupported file type. Please upload a PDF (.pdf) or DOCX (.docx) resume.');
      return;
    }
    if (file.size === 0) {
      setError('Selected file is empty (0 bytes).');
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setError('File exceeds the 5 MB maximum upload limit.');
      return;
    }
    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    validateAndSelectFile(file);
  };

  const handleQuickDemoSignIn = async () => {
    setAuthenticatingDemo(true);
    setError('');
    try {
      await login('alex.rivera@university.edu', 'demo-password-2026');
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          'Unable to authenticate with backend. Ensure FastAPI is running on port 8000.',
      );
    } finally {
      setAuthenticatingDemo(false);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a PDF or DOCX resume file first.');
      return;
    }
    if (!authToken) {
      setError('Please sign in first to securely upload and analyze your resume.');
      return;
    }

    setError('');
    setDuplicateInfo(null);
    setIsUploading(true);

    try {
      const detail = await uploadResumeFile(selectedFile);
      setCurrentDetail(detail);
      syncLiveResumeAnalysis(detail);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      notify(`Resume "${detail.file_name}" analyzed with NLP pipeline`);
      await loadHistory();
    } catch (err) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 409 && detail && typeof detail === 'object') {
        setDuplicateInfo(detail);
        setError(detail.message || 'Duplicate resume already uploaded.');
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Resume upload failed. Check that the backend server is running.');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectHistoryItem = async (resumeId) => {
    setError('');
    setDuplicateInfo(null);
    try {
      const detail = await fetchResumeDetail(resumeId);
      setCurrentDetail(detail);
      syncLiveResumeAnalysis(detail);
      notify(`Loaded analysis for "${detail.file_name}"`, 'info');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load resume analysis.');
    }
  };

  const handleDeleteResume = async (resumeId) => {
    try {
      const res = await deleteResumeById(resumeId);
      notify(res.message || 'Resume deleted', 'info');
      const remaining = history.filter((item) => item.id !== resumeId);
      setHistory(remaining);
      if (currentDetail?.id === resumeId) {
        if (remaining.length > 0) {
          const nextDetail = await fetchResumeDetail(remaining[0].id);
          setCurrentDetail(nextDetail);
          syncLiveResumeAnalysis(nextDetail);
        } else {
          setCurrentDetail(null);
          clearResume();
        }
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to delete resume.');
    }
  };

  const handleExtractSnippet = async (e) => {
    e.preventDefault();
    if (!rawSnippet.trim()) return;
    setExtractingSnippet(true);
    setError('');
    try {
      const data = await extractSkillsFromText(rawSnippet);
      setSnippetResult(data);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Skill extraction failed.');
    } finally {
      setExtractingSnippet(false);
    }
  };

  const handleExportJson = () => {
    if (!currentDetail) return;
    const baseName = currentDetail.file_name.replace(/\.[^.]+$/, '');
    triggerFileDownload(
      JSON.stringify(currentDetail, null, 2),
      `${baseName}_analysis.json`,
      'application/json',
    );
    notify('Downloaded JSON analysis report');
  };

  const handleExportMarkdown = () => {
    if (!currentDetail) return;
    const baseName = currentDetail.file_name.replace(/\.[^.]+$/, '');
    triggerFileDownload(
      buildMarkdownReport(currentDetail),
      `${baseName}_analysis.md`,
      'text/markdown;charset=utf-8',
    );
    notify('Downloaded Markdown analysis report');
  };

  const toggleEvidence = (skillName) => {
    setExpandedEvidence((prev) => ({ ...prev, [skillName]: !prev[skillName] }));
  };

  const analysis = currentDetail?.analysis;

  return (
    <div className="space-y-6">
      {/* Authentication Gate Notice if user doesn't yet have a backend JWT */}
      {!authToken && (
        <section className="flex flex-col justify-between gap-4 rounded-2xl border border-amber-200 bg-amber-50/80 p-5 sm:flex-row sm:items-center">
          <div className="flex items-start gap-3">
            <Lock className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            <div>
              <h2 className="text-sm font-semibold text-amber-950">
                Sign in required to upload resumes
              </h2>
              <p className="mt-0.5 text-xs text-amber-800">
                Resume uploads are securely scoped to your authenticated account. Sign in
                to run live PyMuPDF / python-docx &amp; NLP extraction.
              </p>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              onClick={handleQuickDemoSignIn}
              disabled={authenticatingDemo}
              className="rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-60"
            >
              {authenticatingDemo ? 'Signing in...' : 'Sign In (Demo Student)'}
            </button>
            <Link
              to="/login"
              className="rounded-lg border border-amber-300 bg-white px-3.5 py-2 text-xs font-semibold text-amber-900 hover:bg-amber-100"
            >
              Login Page
            </Link>
          </div>
        </section>
      )}

      {/* Upload & Dropzone Section */}
      <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900">
                AI Resume Analyzer &amp; NLP Skill Extractor
              </h2>
              <DemoBadge mode="live" label="Live FastAPI + spaCy/NLTK" />
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Upload a text-based PDF or DOCX resume (max 5 MB). Files are validated,
              stored privately, parsed with PyMuPDF/python-docx, and analyzed for
              evidence-backed skills.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowTextExtractor((v) => !v)}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{showTextExtractor ? 'Hide Quick Text Extractor' : 'Quick Skill Extractor'}</span>
          </button>
        </div>

        {/* Drag-and-drop Upload Area */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click();
          }}
          className={`mt-5 flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-9 text-center transition ${
            isDragging
              ? 'border-indigo-500 bg-indigo-50/70'
              : 'border-slate-300 bg-[#F8FAFC] hover:border-indigo-400 hover:bg-slate-50'
          }`}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-indigo-600 shadow-xs ring-1 ring-slate-200">
            <UploadCloud className="h-6 w-6" />
          </div>
          <p className="mt-3.5 text-sm font-semibold text-slate-900">
            Drag and drop your PDF or DOCX resume here, or click to browse
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Accepted formats: <span className="font-medium text-slate-700">.PDF</span> and{' '}
            <span className="font-medium text-slate-700">.DOCX</span> · Max size:{' '}
            <span className="font-medium text-slate-700">5 MB</span>
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            className="hidden"
            onChange={(e) => validateAndSelectFile(e.target.files?.[0])}
          />
        </div>

        {/* Error & Duplicate Upload Banner */}
        {error && (
          <div className="mt-4 flex flex-col justify-between gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-800 sm:flex-row sm:items-center">
            <div className="flex items-start gap-2">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
              <span className="font-medium">{error}</span>
            </div>
            {duplicateInfo?.existing_resume_id && (
              <button
                type="button"
                onClick={() => handleSelectHistoryItem(duplicateInfo.existing_resume_id)}
                className="shrink-0 rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-700"
              >
                Open Existing Analysis
              </button>
            )}
          </div>
        )}

        {/* Selected File Card + Upload CTA */}
        {selectedFile && (
          <div className="mt-4 flex flex-col justify-between gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                <FileText className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-slate-900">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-500">
                  {selectedFile.name.toLowerCase().endsWith('.docx') ? 'DOCX' : 'PDF'} ·{' '}
                  {Math.max(1, Math.round(selectedFile.size / 1024))} KB
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  setSelectedFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                disabled={isUploading}
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
              >
                Remove
              </button>
              <button
                type="button"
                onClick={handleUploadAndAnalyze}
                disabled={isUploading || !authToken}
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:opacity-60"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Extracting &amp; Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Upload &amp; Analyze</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Quick Text Skill Extraction Drawer (POST /api/skills/extract) */}
        {showTextExtractor && (
          <div className="mt-5 rounded-xl border border-indigo-200 bg-indigo-50/40 p-4">
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-indigo-950">
                Test Live NLP Skill Extraction{' '}
                <code className="ml-1 rounded bg-white px-1.5 py-0.5 font-mono text-[11px] font-medium text-indigo-700 ring-1 ring-indigo-200">
                  POST /api/skills/extract
                </code>
              </p>
              <span className="text-[11px] text-indigo-700">
                Synonym normalization &amp; anti-false-positive gating
              </span>
            </div>
            <form onSubmit={handleExtractSnippet} className="mt-3 space-y-3">
              <textarea
                rows={3}
                value={rawSnippet}
                onChange={(e) => setRawSnippet(e.target.value)}
                placeholder="Paste resume or project text (e.g., Technical Skills: Python, ML, JS, NLP, React, FastAPI, Docker, AWS)"
                className="w-full rounded-lg border border-slate-300 bg-white p-3 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={extractingSnippet || !authToken || rawSnippet.trim().length < 10}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  {extractingSnippet && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  <span>Extract Skills</span>
                </button>
              </div>
            </form>

            {snippetResult && (
              <div className="mt-3 rounded-lg border border-slate-200 bg-white p-3.5">
                <p className="text-xs font-semibold text-slate-900">
                  Confirmed Skills ({snippetResult.total_confirmed})
                </p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {snippetResult.technical_skills.length === 0 &&
                  snippetResult.soft_skills.length === 0 ? (
                    <span className="text-xs text-slate-500">
                      No confirmed technical or soft skills found in that snippet.
                    </span>
                  ) : (
                    [...snippetResult.technical_skills, ...snippetResult.soft_skills].map(
                      (s) => (
                        <span
                          key={s.name}
                          title={s.evidence?.[0] || ''}
                          className="rounded-md border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[11px] font-medium text-indigo-800"
                        >
                          {s.name} · {s.category} ({Math.round(s.confidence * 100)}%)
                        </span>
                      ),
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Uploaded Resume History Strip */}
      {authToken && (
        <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-indigo-600" />
              <h3 className="text-sm font-semibold text-slate-900">
                Your Uploaded Resumes ({history.length})
              </h3>
            </div>
            {loadingHistory && (
              <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Loading history...
              </span>
            )}
          </div>

          {history.length === 0 ? (
            <p className="mt-3 text-xs text-slate-500">
              No resumes stored in your account yet. Upload a PDF or DOCX above to begin.
            </p>
          ) : (
            <div className="mt-3 grid grid-cols-1 gap-2.5 md:grid-cols-2 lg:grid-cols-3">
              {history.map((item) => {
                const isSelected = currentDetail?.id === item.id;
                return (
                  <div
                    key={item.id}
                    className={`flex items-center justify-between gap-2 rounded-xl border p-3 transition ${
                      isSelected
                        ? 'border-indigo-400 bg-indigo-50/60'
                        : 'border-slate-200 bg-[#F8FAFC] hover:border-slate-300'
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => handleSelectHistoryItem(item.id)}
                      className="min-w-0 flex-1 text-left"
                    >
                      <p className="truncate text-xs font-semibold text-slate-900">
                        {item.file_name}
                      </p>
                      <p className="mt-0.5 text-[11px] text-slate-500">
                        {item.file_type} · {item.technical_skill_count} skills · Score{' '}
                        {item.ats_score}/100
                      </p>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleDeleteResume(item.id)}
                      className="rounded-lg p-1.5 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
                      title="Delete resume"
                      aria-label={`Delete ${item.file_name}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}

      {/* Results Section or Empty State */}
      {!currentDetail || !analysis ? (
        <EmptyState
          icon={FileText}
          title="No resume analysis selected"
          description="Upload a real PDF or DOCX resume above to inspect extracted technical skills, soft skills, education, work experience, projects, and evidence snippets."
          actionLabel="Choose Resume File"
          onAction={() => fileInputRef.current?.click()}
        />
      ) : (
        <div className="space-y-6">
          {/* File Metadata, Extraction Status & Export Controls */}
          <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
            <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
              <div className="flex items-start gap-3.5">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                  <FileCheck2 className="h-6 w-6" />
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-base font-bold text-slate-950">
                      {currentDetail.file_name}
                    </h3>
                    <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-700 uppercase">
                      <CheckCircle2 className="h-3 w-3" />
                      {currentDetail.extraction_status}
                    </span>
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span>{currentDetail.file_type}</span>
                    {currentDetail.file_size_bytes && (
                      <span>{Math.max(1, Math.round(currentDetail.file_size_bytes / 1024))} KB</span>
                    )}
                    {currentDetail.page_count && <span>{currentDetail.page_count} page(s)</span>}
                    <span>{analysis.summary.word_count} cleaned words</span>
                    <span className="inline-flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(currentDetail.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={handleExportMarkdown}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Export Report (.md)</span>
                </button>
                <button
                  type="button"
                  onClick={handleExportJson}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>JSON</span>
                </button>
                <Link
                  to="/skill-gaps"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700"
                >
                  <span>Skill Gap Analysis</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>

            {/* Summary Metrics + Privacy Guard */}
            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-3.5">
                <p className="text-[11px] font-medium text-slate-500">Resume Structure Score</p>
                <p className="mt-1 text-2xl font-bold text-indigo-600 tabular-nums">
                  {analysis.summary.ats_score}
                  <span className="text-xs font-normal text-slate-400">/100</span>
                </p>
              </div>
              <div className="rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-3.5">
                <p className="text-[11px] font-medium text-slate-500">Technical Skills</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 tabular-nums">
                  {analysis.technical_skills.length}
                </p>
              </div>
              <div className="rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-3.5">
                <p className="text-[11px] font-medium text-slate-500">Soft Skills</p>
                <p className="mt-1 text-2xl font-bold text-purple-600 tabular-nums">
                  {analysis.soft_skills.length}
                </p>
              </div>
              <div className="rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-3.5">
                <p className="text-[11px] font-medium text-slate-500">Privacy Protection</p>
                <p className="mt-1.5 inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                  <ShieldCheck className="h-4 w-4" />
                  <span>PII Redacted</span>
                </p>
                <p className="mt-0.5 truncate text-[11px] text-slate-500">
                  {[
                    analysis.personal_info.name_detected && `Name: ${analysis.personal_info.masked_name}`,
                    analysis.personal_info.email_detected && analysis.personal_info.masked_email,
                    analysis.personal_info.phone_detected && analysis.personal_info.masked_phone,
                  ]
                    .filter(Boolean)
                    .join(' · ') || 'No raw PII exposed'}
                </p>
              </div>
            </div>

            {/* Recommendations */}
            {analysis.summary.recommendations?.length > 0 && (
              <div className="mt-5 rounded-xl border border-slate-200/70 bg-[#F8FAFC] p-4">
                <p className="text-xs font-semibold text-slate-800">
                  Resume Analysis Summary &amp; Recommendations
                </p>
                <ul className="mt-2 space-y-1.5 text-xs text-slate-600">
                  {analysis.summary.recommendations.map((rec) => (
                    <li key={rec} className="flex items-start gap-2">
                      <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-600" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {/* Technical Skills (with Evidence Snippets) & Soft Skills */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs lg:col-span-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">
                    Confirmed Technical Skills ({analysis.technical_skills.length})
                  </h3>
                  <p className="text-xs text-slate-500">
                    Normalized via skill taxonomy. Click any skill to inspect its source
                    evidence snippet.
                  </p>
                </div>
              </div>

              {analysis.technical_skills.length === 0 ? (
                <p className="mt-4 text-xs text-slate-500">
                  No confirmed technical skills matched the taxonomy in this document.
                </p>
              ) : (
                <div className="mt-5 space-y-5">
                  {Object.entries(analysis.skills_by_category || {}).map(([category, skills]) => (
                    <div key={category}>
                      <p className="mb-2 text-xs font-semibold tracking-wide text-slate-500 uppercase">
                        {category} ({skills.length})
                      </p>
                      <div className="space-y-2">
                        {skills.map((skill) => {
                          const isOpen = Boolean(expandedEvidence[skill.name]);
                          return (
                            <div
                              key={skill.name}
                              className="rounded-xl border border-slate-200/80 bg-[#F8FAFC] px-3.5 py-2.5"
                            >
                              <button
                                type="button"
                                onClick={() => toggleEvidence(skill.name)}
                                className="flex w-full items-center justify-between gap-3 text-left"
                              >
                                <div className="flex flex-wrap items-center gap-2">
                                  <span className="text-xs font-semibold text-slate-900">
                                    {skill.name}
                                  </span>
                                  {skill.matched_terms?.some(
                                    (t) => t.toLowerCase() !== skill.name.toLowerCase(),
                                  ) && (
                                    <span className="rounded bg-indigo-50 px-1.5 py-0.5 text-[10px] font-medium text-indigo-700">
                                      normalized from {skill.matched_terms.join(', ')}
                                    </span>
                                  )}
                                  <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 ring-1 ring-emerald-200 tabular-nums">
                                    {Math.round(skill.confidence * 100)}%
                                  </span>
                                </div>
                                {isOpen ? (
                                  <ChevronUp className="h-4 w-4 text-slate-400" />
                                ) : (
                                  <ChevronDown className="h-4 w-4 text-slate-400" />
                                )}
                              </button>

                              {isOpen && skill.evidence?.length > 0 && (
                                <div className="mt-2.5 space-y-1.5 border-t border-slate-200/80 pt-2.5">
                                  <p className="text-[10px] font-semibold tracking-wide text-slate-500 uppercase">
                                    Evidence from uploaded resume
                                  </p>
                                  {skill.evidence.map((snippet, idx) => (
                                    <p
                                      key={idx}
                                      className="rounded-lg bg-white px-2.5 py-1.5 font-mono text-[11px] text-slate-700 ring-1 ring-slate-200/70"
                                    >
                                      &ldquo;{snippet}&rdquo;
                                    </p>
                                  ))}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-6 lg:col-span-4">
              {/* Soft Skills */}
              <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
                <h3 className="text-sm font-semibold text-slate-900">
                  Soft Skills ({analysis.soft_skills.length})
                </h3>
                <p className="mt-0.5 text-xs text-slate-500">
                  Interpersonal &amp; execution competencies detected in resume text.
                </p>

                <div className="mt-4 space-y-2.5">
                  {analysis.soft_skills.length === 0 ? (
                    <p className="text-xs text-slate-500">
                      No explicit soft skills detected in this resume.
                    </p>
                  ) : (
                    analysis.soft_skills.map((skill) => (
                      <div
                        key={skill.name}
                        className="rounded-xl border border-purple-100 bg-purple-50/40 p-3"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-purple-950">
                            {skill.name}
                          </span>
                          <span className="text-[11px] font-semibold text-purple-700 tabular-nums">
                            {Math.round(skill.confidence * 100)}%
                          </span>
                        </div>
                        {skill.evidence?.[0] && (
                          <p className="mt-1 text-[11px] text-slate-600">
                            &ldquo;{skill.evidence[0]}&rdquo;
                          </p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Certifications */}
              <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
                <div className="flex items-center gap-2">
                  <Award className="h-4 w-4 text-indigo-600" />
                  <h3 className="text-sm font-semibold text-slate-900">
                    Certifications ({analysis.certifications.length})
                  </h3>
                </div>
                {analysis.certifications.length === 0 ? (
                  <p className="mt-3 text-xs text-slate-500">
                    No certifications detected in this resume.
                  </p>
                ) : (
                  <ul className="mt-3 space-y-2 text-xs text-slate-700">
                    {analysis.certifications.map((cert) => (
                      <li
                        key={cert}
                        className="rounded-lg border border-slate-100 bg-[#F8FAFC] px-3 py-2"
                      >
                        {cert}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </section>

          {/* Education, Experience, and Projects */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Education */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <GraduationCap className="h-4 w-4 text-indigo-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Extracted Education ({analysis.education.length})
                </h3>
              </div>
              <div className="mt-4 space-y-3">
                {analysis.education.length === 0 ? (
                  <p className="text-xs text-slate-500">
                    No education entries detected.
                  </p>
                ) : (
                  analysis.education.map((edu, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-100 bg-[#F8FAFC] p-3.5"
                    >
                      <p className="text-xs font-semibold text-slate-900">{edu.degree}</p>
                      {edu.institution && (
                        <p className="mt-0.5 text-xs text-slate-600">{edu.institution}</p>
                      )}
                      {edu.period && (
                        <p className="mt-1 text-[11px] font-medium text-indigo-600">
                          {edu.period}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Work Experience */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <Briefcase className="h-4 w-4 text-blue-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Extracted Experience ({analysis.experience.length})
                </h3>
              </div>
              <div className="mt-4 space-y-3">
                {analysis.experience.length === 0 ? (
                  <p className="text-xs text-slate-500">
                    No work experience entries detected.
                  </p>
                ) : (
                  analysis.experience.map((exp, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-100 bg-[#F8FAFC] p-3.5"
                    >
                      <p className="text-xs font-semibold text-slate-900">{exp.role}</p>
                      {(exp.organization || exp.duration) && (
                        <p className="mt-0.5 text-[11px] text-slate-500">
                          {[exp.organization, exp.duration].filter(Boolean).join(' · ')}
                        </p>
                      )}
                      {exp.highlights?.length > 0 && (
                        <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] text-slate-600">
                          {exp.highlights.map((hl, i) => (
                            <li key={i}>{hl}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Projects */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <FolderGit2 className="h-4 w-4 text-purple-600" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Extracted Projects ({analysis.projects.length})
                </h3>
              </div>
              <div className="mt-4 space-y-3">
                {analysis.projects.length === 0 ? (
                  <p className="text-xs text-slate-500">No projects section detected.</p>
                ) : (
                  analysis.projects.map((proj, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-100 bg-[#F8FAFC] p-3.5"
                    >
                      <p className="text-xs font-semibold text-slate-900">{proj.title}</p>
                      {proj.description && (
                        <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
                          {proj.description}
                        </p>
                      )}
                      {proj.technologies?.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {proj.technologies.map((tech) => (
                            <span
                              key={tech}
                              className="rounded bg-white px-2 py-0.5 text-[10px] font-medium text-indigo-700 ring-1 ring-indigo-100"
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
