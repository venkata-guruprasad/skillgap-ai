import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  Briefcase,
  CheckCircle2,
  Compass,
  Cpu,
  Database,
  FileText,
  GitCompare,
  GraduationCap,
  Layers,
  Map,
  Menu,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  X,
} from 'lucide-react';
import logo from '../assets/logo.svg';
import { useApp } from '../context/AppContext';

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Upload Your Resume',
    description:
      'Drop your PDF or DOCX resume to parse sections, projects, and technical competencies automatically.',
    icon: FileText,
  },
  {
    step: '02',
    title: 'Benchmark Skill Gaps',
    description:
      'Compare extracted skills against real industry role requirements to spot missing high-priority competencies.',
    icon: GitCompare,
  },
  {
    step: '03',
    title: 'Predict Career Fit',
    description:
      'Discover ranked career tracks with transparent compatibility scores and clear role-fit explanations.',
    icon: Compass,
  },
  {
    step: '04',
    title: 'Execute Your Roadmap',
    description:
      'Follow structured 30, 60, or 90-day learning milestones and track measurable weekly readiness.',
    icon: Map,
  },
];

const FEATURES = [
  {
    title: 'Resume Analyzer',
    description:
      'Structured extraction of skills, ATS signals, and actionable improvement suggestions from PDF and DOCX files.',
    icon: FileText,
    to: '/resume-analyzer',
  },
  {
    title: 'Skill Gap Analysis',
    description:
      'Side-by-side breakdown of matched, missing, and bonus transferable skills against any target engineering role.',
    icon: GitCompare,
    to: '/skill-gaps',
  },
  {
    title: 'AI Career Prediction',
    description:
      'Ranked career recommendations showing compatibility percentages, market demand, and why each path aligns with you.',
    icon: Compass,
    to: '/career-prediction',
  },
  {
    title: 'Job Explorer',
    description:
      'Filter curated internships and full-time roles by work mode, level, and real-time compatibility score.',
    icon: Briefcase,
    to: '/jobs',
  },
  {
    title: 'AI Learning Roadmap',
    description:
      'Interactive 30, 60, and 90-day milestone timelines with task checkboxes and curated technical resources.',
    icon: Map,
    to: '/roadmap',
  },
  {
    title: 'Progress Tracking',
    description:
      'Monitor study velocity, completed milestones, and rising career readiness across every skill domain.',
    icon: TrendingUp,
    to: '/progress',
  },
];

const BENEFITS = [
  {
    audience: 'For Students & Graduates',
    title: 'Replace career guesswork with clear evidence',
    points: [
      'Know exactly which 3–4 skills separate you from your target internship or role.',
      'Turn unstructured learning into trackable 30/60/90-day milestones.',
      'Focus applications on jobs where your skill compatibility is highest.',
    ],
    icon: GraduationCap,
  },
  {
    audience: 'For Career Switchers',
    title: 'Surface transferable strengths immediately',
    points: [
      'Identify adjacent high-growth roles where existing skills carry strong weight.',
      'Compare multiple tracks side by side with transparent gap explanations.',
      'Quantify readiness gains week over week before interviewing.',
    ],
    icon: Target,
  },
  {
    audience: 'For Mentors & Universities',
    title: 'Structured visibility into cohort readiness',
    points: [
      'Standardized skill taxonomies aligned with modern industry role profiles.',
      'Clear radar and gap visuals that make advising sessions actionable.',
      'Modular open architecture built on FastAPI, React, and PostgreSQL.',
    ],
    icon: BarChart3,
  },
];

const TECH_STACK = [
  { name: 'React & Vite', role: 'Fast, responsive SaaS frontend', icon: Layers },
  { name: 'Tailwind CSS & Recharts', role: 'Design system & analytics visuals', icon: BarChart3 },
  { name: 'FastAPI & Pydantic', role: 'High-performance Python API layer', icon: Cpu },
  { name: 'PostgreSQL & Alembic', role: 'Relational persistence & migrations', icon: Database },
  { name: 'spaCy, NLTK & SBERT', role: 'Planned NLP & semantic matching stack', icon: Sparkles },
  { name: 'Docker & Compose', role: 'Reproducible multi-service deployment', icon: ShieldCheck },
];

export default function LandingPage() {
  const { isAuthenticated, health } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* Top Navbar */}
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/95 backdrop-blur-xs">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2.5">
            <img src={logo} alt="SkillGap AI" className="h-8 w-8 rounded-lg" />
            <span className="text-base font-bold tracking-tight text-slate-900">
              SkillGap AI
            </span>
          </Link>

          <nav className="hidden items-center gap-7 text-sm font-medium text-slate-600 md:flex">
            <button
              type="button"
              onClick={() => scrollToSection('how-it-works')}
              className="transition hover:text-slate-900"
            >
              How It Works
            </button>
            <button
              type="button"
              onClick={() => scrollToSection('features')}
              className="transition hover:text-slate-900"
            >
              Features
            </button>
            <button
              type="button"
              onClick={() => scrollToSection('benefits')}
              className="transition hover:text-slate-900"
            >
              Benefits
            </button>
            <button
              type="button"
              onClick={() => scrollToSection('technology')}
              className="transition hover:text-slate-900"
            >
              Technology
            </button>
          </nav>

          <div className="hidden items-center gap-3 md:flex">
            {isAuthenticated ? (
              <>
                <Link
                  to="/login"
                  className="rounded-lg px-3.5 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
                >
                  Sign In
                </Link>
                <Link
                  to="/dashboard"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-xs transition hover:bg-indigo-700"
                >
                  <span>Open Dashboard</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-lg px-3.5 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-xs transition hover:bg-indigo-700"
                >
                  <span>Get Started</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </>
            )}
          </div>

          <button
            type="button"
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="border-t border-slate-200 bg-white px-4 py-4 md:hidden">
            <div className="flex flex-col space-y-2 text-sm font-medium text-slate-700">
              <button
                type="button"
                onClick={() => scrollToSection('how-it-works')}
                className="rounded-lg px-3 py-2 text-left hover:bg-slate-50"
              >
                How It Works
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('features')}
                className="rounded-lg px-3 py-2 text-left hover:bg-slate-50"
              >
                Features
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('benefits')}
                className="rounded-lg px-3 py-2 text-left hover:bg-slate-50"
              >
                Benefits
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('technology')}
                className="rounded-lg px-3 py-2 text-left hover:bg-slate-50"
              >
                Technology
              </button>
              <div className="flex gap-2 pt-2">
                <Link
                  to="/login"
                  className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-center text-slate-700"
                >
                  Sign In
                </Link>
                <Link
                  to="/dashboard"
                  className="flex-1 rounded-lg bg-indigo-600 px-3 py-2 text-center text-white"
                >
                  Dashboard
                </Link>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="border-b border-slate-200/80 bg-[#F8FAFC]">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-12">
            <div className="lg:col-span-7">
              <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                <Sparkles className="h-3.5 w-3.5" />
                <span>AI-Powered Career Guidance Platform</span>
              </div>

              <h1 className="mt-5 text-4xl font-extrabold tracking-tight text-slate-950 sm:text-5xl lg:text-[3.25rem] lg:leading-[1.1]">
                Discover Your Skills. Predict Your Career. Build Your Future.
              </h1>

              <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
                Analyze your resume, discover missing industry skills, explore career
                opportunities, and build personalized AI-powered learning roadmaps.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3.5">
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-xs transition hover:bg-indigo-700"
                >
                  <span>Get Started</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>

                <button
                  type="button"
                  onClick={() => scrollToSection('features')}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-800 shadow-xs transition hover:border-slate-400 hover:bg-slate-50"
                >
                  <span>Explore Features</span>
                </button>

                <Link
                  to="/dashboard"
                  className="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-indigo-600 transition hover:text-indigo-700"
                >
                  <span>Live Workspace Preview</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              <div className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs font-medium text-slate-500">
                <span className="inline-flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  PDF &amp; DOCX resume ready
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Transparent role compatibility
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  30 / 60 / 90-day roadmaps
                </span>
              </div>
            </div>

            {/* Clean SaaS Product Preview Card */}
            <div className="lg:col-span-5">
              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-md">
                <div className="flex items-center justify-between border-b border-slate-100 bg-[#0B1120] px-5 py-3.5 text-white">
                  <div className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-full bg-rose-400" />
                    <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
                    <span className="ml-2 text-xs font-medium text-slate-300">
                      SkillGap AI Workspace
                    </span>
                  </div>
                  <span className="rounded-full bg-indigo-500/20 px-2.5 py-0.5 text-[11px] font-medium text-indigo-300">
                    Preview
                  </span>
                </div>

                <div className="space-y-4 p-5">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5">
                      <p className="text-[11px] font-medium text-slate-500">
                        Top Career Match
                      </p>
                      <p className="mt-1 text-2xl font-bold text-indigo-600 tabular-nums">
                        73%
                      </p>
                      <p className="mt-0.5 text-xs font-medium text-slate-700">
                        Full-Stack Engineer
                      </p>
                    </div>
                    <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5">
                      <p className="text-[11px] font-medium text-slate-500">
                        Extracted Skills
                      </p>
                      <p className="mt-1 text-2xl font-bold text-slate-900 tabular-nums">
                        12
                      </p>
                      <p className="mt-0.5 text-xs font-medium text-emerald-600">
                        3 priority gaps found
                      </p>
                    </div>
                  </div>

                  <div className="rounded-xl border border-slate-200/80 p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-800">
                        Role Readiness Breakdown
                      </span>
                      <span className="text-[11px] font-medium text-purple-600">
                        AI Benchmark
                      </span>
                    </div>
                    <div className="mt-3 space-y-2.5">
                      {[
                        { label: 'Full-Stack Software Engineer', pct: 73, color: 'bg-indigo-600' },
                        { label: 'Frontend Product Engineer', pct: 60, color: 'bg-blue-600' },
                        { label: 'Backend API Engineer', pct: 56, color: 'bg-purple-600' },
                      ].map((row) => (
                        <div key={row.label}>
                          <div className="flex justify-between text-xs">
                            <span className="font-medium text-slate-700">{row.label}</span>
                            <span className="font-semibold text-slate-900 tabular-nums">
                              {row.pct}%
                            </span>
                          </div>
                          <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                            <div
                              className={`h-full rounded-full ${row.color}`}
                              style={{ width: `${row.pct}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                    <div>
                      <p className="text-xs font-semibold text-slate-800">
                        Priority Gaps Identified
                      </p>
                      <div className="mt-1.5 flex flex-wrap gap-1.5">
                        {['Docker', 'TypeScript', 'CI/CD'].map((skill) => (
                          <span
                            key={skill}
                            className="rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-[11px] font-medium text-rose-700"
                          >
                            + {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <Link
                      to="/roadmap"
                      className="shrink-0 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-slate-800"
                    >
                      View Plan
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="border-b border-slate-200/80 bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold tracking-wider text-indigo-600 uppercase">
              How It Works
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              From raw resume to an actionable career blueprint
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              Four streamlined steps turn your existing skills into measurable role readiness.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {HOW_IT_WORKS.map(({ step, title, description, icon: Icon }) => (
              <div
                key={step}
                className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs transition hover:border-indigo-200 hover:shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-400">
                    STEP {step}
                  </span>
                </div>
                <h3 className="mt-5 text-base font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-b border-slate-200/80 bg-[#F8FAFC] py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold tracking-wider text-blue-600 uppercase">
              Platform Capabilities
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              Everything you need to close skill gaps with confidence
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              Explore every module built into the SkillGap AI workspace.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ title, description, icon: Icon, to }) => (
              <Link
                key={title}
                to={to}
                className="group flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md"
              >
                <div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition group-hover:bg-indigo-600 group-hover:text-white">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-4 text-base font-semibold text-slate-900">
                    {title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">
                    {description}
                  </p>
                </div>
                <div className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                  <span>Open module</span>
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section id="benefits" className="border-b border-slate-200/80 bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold tracking-wider text-purple-600 uppercase">
              Why SkillGap AI
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              Built for clarity, speed, and measurable career outcomes
            </h2>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-6 lg:grid-cols-3">
            {BENEFITS.map(({ audience, title, points, icon: Icon }) => (
              <div
                key={audience}
                className="rounded-2xl border border-slate-200/80 bg-[#F8FAFC] p-6"
              >
                <div className="inline-flex items-center gap-2 rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-2xs ring-1 ring-slate-200/80">
                  <Icon className="h-4 w-4 text-purple-600" />
                  <span>{audience}</span>
                </div>
                <h3 className="mt-4 text-lg font-bold text-slate-900">{title}</h3>
                <ul className="mt-4 space-y-2.5">
                  {points.map((pt) => (
                    <li
                      key={pt}
                      className="flex items-start gap-2.5 text-sm text-slate-600"
                    >
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section id="technology" className="border-b border-slate-200/80 bg-[#0B1120] py-20 text-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold tracking-wider text-indigo-400 uppercase">
              Architecture &amp; Technology
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-white">
              Engineered on a modern full-stack AI foundation
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-400">
              Clean separation between the React SaaS client, FastAPI service layer,
              PostgreSQL relational models, and modular Python NLP/ML pipelines.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {TECH_STACK.map(({ name, role, icon: Icon }) => (
              <div
                key={name}
                className="flex items-start gap-4 rounded-xl border border-slate-800 bg-slate-900/70 p-5"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-400">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{name}</h3>
                  <p className="mt-1 text-xs text-slate-400">{role}</p>
                </div>
              </div>
            ))}
          </div>

          {/* CTA Banner */}
          <div className="mt-14 flex flex-col items-start justify-between gap-6 rounded-2xl border border-slate-800 bg-slate-900/90 p-8 sm:flex-row sm:items-center">
            <div>
              <h3 className="text-xl font-bold text-white">
                Ready to map your next career move?
              </h3>
              <p className="mt-1 text-sm text-slate-400">
                Create an account or launch the interactive student dashboard now.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500"
              >
                <span>Get Started Free</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-5 py-2.5 text-sm font-semibold text-slate-200 transition hover:bg-slate-800"
              >
                <span>Open Dashboard</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 px-4 sm:flex-row sm:items-center sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <img src={logo} alt="SkillGap AI" className="h-7 w-7 rounded-md" />
            <div>
              <span className="text-sm font-bold text-slate-900">SkillGap AI</span>
              <p className="text-xs text-slate-500">
                AI-Powered Skill Gap &amp; Career Prediction System
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-5 text-xs font-medium text-slate-600">
            <Link to="/dashboard" className="hover:text-slate-900">
              Dashboard
            </Link>
            <Link to="/resume-analyzer" className="hover:text-slate-900">
              Resume Analyzer
            </Link>
            <Link to="/skill-gaps" className="hover:text-slate-900">
              Skill Gaps
            </Link>
            <Link to="/career-prediction" className="hover:text-slate-900">
              Career Prediction
            </Link>
            <Link to="/jobs" className="hover:text-slate-900">
              Job Explorer
            </Link>
            <Link to="/roadmap" className="hover:text-slate-900">
              Roadmap
            </Link>
          </div>

          <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600">
            <span
              className={`h-2 w-2 rounded-full ${
                health.apiHealth.status === 'success' ? 'bg-emerald-500' : 'bg-amber-400'
              }`}
            />
            <span>
              Backend: {health.apiHealth.status === 'success' ? 'Online' : 'Standby'}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
