/**
 * TEMPORARY DEMO DATA MODULE (Phase 2 Frontend Preview)
 * ---------------------------------------------------------------------------
 * Strictly separated from real API calls in `src/services/api.js`.
 * Replace individual dataset imports with live FastAPI endpoints in Phase 3+.
 */

export const IS_DEMO_DATA = true;

export const DEFAULT_USER = {
  id: 'demo-student-01',
  fullName: 'Alex Rivera',
  email: 'alex.rivera@university.edu',
  headline: 'Final-Year Computer Science Student',
  university: 'State Institute of Technology',
  graduationYear: '2026',
  targetRoleId: 'fullstack-engineer',
  weeklyGoalHours: 12,
  bio: 'Passionate about full-stack web engineering, API architecture, and applied machine learning.',
  notifications: {
    weeklyDigest: true,
    jobAlerts: true,
    roadmapReminders: true,
    productUpdates: false,
  },
};

export const INITIAL_USER_SKILLS = [
  { name: 'Python', category: 'Backend', level: 88, confidence: 0.96 },
  { name: 'JavaScript', category: 'Frontend', level: 85, confidence: 0.95 },
  { name: 'React', category: 'Frontend', level: 84, confidence: 0.94 },
  { name: 'Tailwind CSS', category: 'Frontend', level: 82, confidence: 0.91 },
  { name: 'FastAPI', category: 'Backend', level: 74, confidence: 0.89 },
  { name: 'SQL', category: 'Database', level: 78, confidence: 0.92 },
  { name: 'PostgreSQL', category: 'Database', level: 72, confidence: 0.87 },
  { name: 'REST APIs', category: 'Backend', level: 86, confidence: 0.93 },
  { name: 'Git', category: 'Tools & DevOps', level: 90, confidence: 0.97 },
  { name: 'Data Visualization', category: 'Data & AI', level: 70, confidence: 0.84 },
  { name: 'Scikit-learn', category: 'Data & AI', level: 64, confidence: 0.82 },
  { name: 'HTML/CSS', category: 'Frontend', level: 92, confidence: 0.98 },
];

export const INITIAL_RESUME_SUMMARY = {
  fileName: 'Alex_Rivera_CS_Resume_2026.pdf',
  fileSizeKb: 248,
  fileType: 'PDF',
  analyzedAt: '2026-11-17T14:20:00Z',
  atsScore: 84,
  wordCount: 542,
  sectionsDetected: ['Contact Info', 'Education', 'Technical Skills', 'Projects', 'Experience'],
  suggestions: [
    'Quantify backend latency or user impact metrics in project bullet points.',
    'Highlight containerization (Docker) and CI/CD deployment experience.',
    'Add automated testing frameworks (Pytest / Playwright) to technical skills.',
  ],
};

export const CAREER_ROLES = [
  {
    id: 'fullstack-engineer',
    title: 'Full-Stack Software Engineer',
    category: 'Software Engineering',
    avgSalary: '$118,000',
    salaryNum: 118000,
    demand: 'Very High',
    growth: '+22% YoY',
    requiredSkills: [
      { name: 'JavaScript', priority: 'Critical', category: 'Frontend' },
      { name: 'React', priority: 'Critical', category: 'Frontend' },
      { name: 'Python', priority: 'Critical', category: 'Backend' },
      { name: 'FastAPI', priority: 'Important', category: 'Backend' },
      { name: 'PostgreSQL', priority: 'Critical', category: 'Database' },
      { name: 'REST APIs', priority: 'Critical', category: 'Backend' },
      { name: 'Git', priority: 'Important', category: 'Tools & DevOps' },
      { name: 'TypeScript', priority: 'Important', category: 'Frontend' },
      { name: 'Docker', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'CI/CD', priority: 'Important', category: 'Tools & DevOps' },
      { name: 'Automated Testing', priority: 'Nice-to-have', category: 'Tools & DevOps' },
    ],
    explanation:
      'Strong alignment with both modern React frontend architecture and Python/FastAPI API development. Closing gaps in Docker, TypeScript, and CI/CD pipelines will make your profile production-ready.',
  },
  {
    id: 'backend-engineer',
    title: 'Backend API Engineer',
    category: 'Software Engineering',
    avgSalary: '$126,000',
    salaryNum: 126000,
    demand: 'High',
    growth: '+19% YoY',
    requiredSkills: [
      { name: 'Python', priority: 'Critical', category: 'Backend' },
      { name: 'FastAPI', priority: 'Critical', category: 'Backend' },
      { name: 'PostgreSQL', priority: 'Critical', category: 'Database' },
      { name: 'SQL', priority: 'Critical', category: 'Database' },
      { name: 'REST APIs', priority: 'Critical', category: 'Backend' },
      { name: 'Docker', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'Redis', priority: 'Important', category: 'Database' },
      { name: 'System Design', priority: 'Critical', category: 'Backend' },
      { name: 'CI/CD', priority: 'Important', category: 'Tools & DevOps' },
      { name: 'Kubernetes', priority: 'Nice-to-have', category: 'Tools & DevOps' },
    ],
    explanation:
      'Your Python, SQL, PostgreSQL, and REST API foundation already covers core backend responsibilities. Adding distributed caching (Redis), Docker, and system design elevates you into mid-level roles.',
  },
  {
    id: 'frontend-engineer',
    title: 'Frontend Product Engineer',
    category: 'Software Engineering',
    avgSalary: '$112,000',
    salaryNum: 112000,
    demand: 'High',
    growth: '+16% YoY',
    requiredSkills: [
      { name: 'JavaScript', priority: 'Critical', category: 'Frontend' },
      { name: 'React', priority: 'Critical', category: 'Frontend' },
      { name: 'Tailwind CSS', priority: 'Important', category: 'Frontend' },
      { name: 'HTML/CSS', priority: 'Critical', category: 'Frontend' },
      { name: 'REST APIs', priority: 'Important', category: 'Backend' },
      { name: 'Git', priority: 'Important', category: 'Tools & DevOps' },
      { name: 'TypeScript', priority: 'Critical', category: 'Frontend' },
      { name: 'Next.js', priority: 'Important', category: 'Frontend' },
      { name: 'Accessibility (a11y)', priority: 'Important', category: 'Frontend' },
      { name: 'Automated Testing', priority: 'Nice-to-have', category: 'Tools & DevOps' },
    ],
    explanation:
      'Excellent match on React, JavaScript, Tailwind CSS, and UI engineering fundamentals. Prioritizing TypeScript and Next.js unlocks senior product engineering tracks.',
  },
  {
    id: 'ml-engineer',
    title: 'Machine Learning Engineer',
    category: 'Data & AI',
    avgSalary: '$146,000',
    salaryNum: 146000,
    demand: 'Very High',
    growth: '+34% YoY',
    requiredSkills: [
      { name: 'Python', priority: 'Critical', category: 'Backend' },
      { name: 'Scikit-learn', priority: 'Critical', category: 'Data & AI' },
      { name: 'SQL', priority: 'Important', category: 'Database' },
      { name: 'FastAPI', priority: 'Important', category: 'Backend' },
      { name: 'PyTorch', priority: 'Critical', category: 'Data & AI' },
      { name: 'NLP / Transformers', priority: 'Critical', category: 'Data & AI' },
      { name: 'MLOps', priority: 'Important', category: 'Tools & DevOps' },
      { name: 'Docker', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'Feature Engineering', priority: 'Important', category: 'Data & AI' },
      { name: 'Cloud AWS/GCP', priority: 'Nice-to-have', category: 'Tools & DevOps' },
    ],
    explanation:
      'Solid Python, FastAPI, and Scikit-learn starting point for model serving. To compete for ML Engineer roles, build hands-on depth in PyTorch, Transformers, and Dockerized MLOps pipelines.',
  },
  {
    id: 'data-scientist',
    title: 'Applied Data Scientist',
    category: 'Data & AI',
    avgSalary: '$132,000',
    salaryNum: 132000,
    demand: 'High',
    growth: '+25% YoY',
    requiredSkills: [
      { name: 'Python', priority: 'Critical', category: 'Backend' },
      { name: 'SQL', priority: 'Critical', category: 'Database' },
      { name: 'Scikit-learn', priority: 'Critical', category: 'Data & AI' },
      { name: 'Data Visualization', priority: 'Critical', category: 'Data & AI' },
      { name: 'PostgreSQL', priority: 'Important', category: 'Database' },
      { name: 'Statistics & A/B Testing', priority: 'Critical', category: 'Data & AI' },
      { name: 'Pandas & NumPy', priority: 'Critical', category: 'Data & AI' },
      { name: 'NLP / Transformers', priority: 'Nice-to-have', category: 'Data & AI' },
      { name: 'Feature Engineering', priority: 'Important', category: 'Data & AI' },
    ],
    explanation:
      'Strong analytical base across Python, SQL, visualization, and Scikit-learn. Strengthening statistical experimentation (A/B testing) and feature engineering will bridge the remaining gap.',
  },
  {
    id: 'devops-cloud',
    title: 'Cloud & DevOps Engineer',
    category: 'Infrastructure',
    avgSalary: '$134,000',
    salaryNum: 134000,
    demand: 'High',
    growth: '+21% YoY',
    requiredSkills: [
      { name: 'Python', priority: 'Important', category: 'Backend' },
      { name: 'Git', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'PostgreSQL', priority: 'Important', category: 'Database' },
      { name: 'Docker', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'Kubernetes', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'CI/CD', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'Terraform', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'Cloud AWS/GCP', priority: 'Critical', category: 'Tools & DevOps' },
      { name: 'Linux Administration', priority: 'Important', category: 'Tools & DevOps' },
    ],
    explanation:
      'Scripting and Git skills translate well, but core infrastructure skills (Docker, Kubernetes, Terraform, and Cloud platforms) require focused upskilling before targeting DevOps roles.',
  },
];

export const RADAR_BENCHMARK_DATA = [
  { domain: 'Frontend', student: 86, benchmark: 88 },
  { domain: 'Backend', student: 81, benchmark: 85 },
  { domain: 'Database', student: 75, benchmark: 82 },
  { domain: 'Data & AI', student: 67, benchmark: 80 },
  { domain: 'Cloud & DevOps', student: 52, benchmark: 84 },
  { domain: 'Testing & QA', student: 58, benchmark: 78 },
];

export const WEEKLY_LEARNING_DATA = [
  { week: 'Wk 1', hours: 6.5, tasksCompleted: 3, readiness: 64 },
  { week: 'Wk 2', hours: 8.0, tasksCompleted: 5, readiness: 68 },
  { week: 'Wk 3', hours: 9.5, tasksCompleted: 6, readiness: 72 },
  { week: 'Wk 4', hours: 7.5, tasksCompleted: 4, readiness: 74 },
  { week: 'Wk 5', hours: 11.0, tasksCompleted: 7, readiness: 79 },
  { week: 'Wk 6', hours: 12.5, tasksCompleted: 8, readiness: 83 },
];

export const JOB_LISTINGS = [
  {
    id: 'job-1',
    title: 'Junior Full-Stack Engineer',
    company: 'Linearity Labs',
    location: 'San Francisco, CA',
    workMode: 'Hybrid',
    level: 'Entry',
    salary: '$105k – $128k',
    postedAgo: '2 days ago',
    roleId: 'fullstack-engineer',
    requiredSkills: ['React', 'JavaScript', 'Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Git'],
    description:
      'Build responsive analytics interfaces in React and high-throughput FastAPI microservices backed by PostgreSQL.',
  },
  {
    id: 'job-2',
    title: 'Frontend Product Engineer (React)',
    company: 'StripeFlow Systems',
    location: 'Remote (US / Global)',
    workMode: 'Remote',
    level: 'Entry',
    salary: '$100k – $122k',
    postedAgo: '1 day ago',
    roleId: 'frontend-engineer',
    requiredSkills: ['React', 'JavaScript', 'Tailwind CSS', 'TypeScript', 'REST APIs', 'Git'],
    description:
      'Craft crisp, accessible SaaS dashboards and interactive visualization workflows for enterprise customers.',
  },
  {
    id: 'job-3',
    title: 'Python Backend Developer',
    company: 'Veridian Cloud',
    location: 'Austin, TX',
    workMode: 'Hybrid',
    level: 'Mid',
    salary: '$118k – $140k',
    postedAgo: '3 days ago',
    roleId: 'backend-engineer',
    requiredSkills: ['Python', 'FastAPI', 'PostgreSQL', 'SQL', 'REST APIs', 'Docker', 'Redis'],
    description:
      'Design and scale REST APIs, database schemas, and caching layers for high-volume data ingestion services.',
  },
  {
    id: 'job-4',
    title: 'Associate ML & NLP Engineer',
    company: 'Cortexa AI',
    location: 'New York, NY',
    workMode: 'Hybrid',
    level: 'Entry',
    salary: '$125k – $150k',
    postedAgo: '4 days ago',
    roleId: 'ml-engineer',
    requiredSkills: ['Python', 'Scikit-learn', 'FastAPI', 'PyTorch', 'NLP / Transformers', 'Docker'],
    description:
      'Train and deploy semantic embedding pipelines and text classification models into production APIs.',
  },
  {
    id: 'job-5',
    title: 'Data Science Intern – Product Analytics',
    company: 'MetricPulse',
    location: 'Remote',
    workMode: 'Remote',
    level: 'Intern',
    salary: '$45/hr – $55/hr',
    postedAgo: '5 hours ago',
    roleId: 'data-scientist',
    requiredSkills: ['Python', 'SQL', 'Data Visualization', 'Scikit-learn', 'Statistics & A/B Testing'],
    description:
      'Partner with product managers to run funnel experiments, build dashboards, and model user retention.',
  },
  {
    id: 'job-6',
    title: 'Software Engineer – Developer Tools',
    company: 'Northstar Dev',
    location: 'Seattle, WA',
    workMode: 'On-site',
    level: 'Mid',
    salary: '$130k – $155k',
    postedAgo: '6 days ago',
    roleId: 'fullstack-engineer',
    requiredSkills: ['React', 'TypeScript', 'Python', 'PostgreSQL', 'CI/CD', 'Docker', 'Automated Testing'],
    description:
      'Own full-stack workflows, automated CI/CD checks, and developer telemetry dashboards.',
  },
  {
    id: 'job-7',
    title: 'Cloud Infrastructure Engineer',
    company: 'Nimbus Ops',
    location: 'Denver, CO',
    workMode: 'Remote',
    level: 'Mid',
    salary: '$128k – $148k',
    postedAgo: '1 week ago',
    roleId: 'devops-cloud',
    requiredSkills: ['Docker', 'Kubernetes', 'Terraform', 'CI/CD', 'Cloud AWS/GCP', 'Python'],
    description:
      'Automate multi-region Kubernetes deployments, observability stacks, and infrastructure-as-code.',
  },
  {
    id: 'job-8',
    title: 'Full-Stack Engineering Intern',
    company: 'CanvasAI',
    location: 'Boston, MA',
    workMode: 'Hybrid',
    level: 'Intern',
    salary: '$42/hr – $50/hr',
    postedAgo: '1 day ago',
    roleId: 'fullstack-engineer',
    requiredSkills: ['React', 'JavaScript', 'Tailwind CSS', 'Python', 'REST APIs', 'Git'],
    description:
      'Ship user-facing product features end-to-end with mentorship from senior engineers.',
  },
];

export const ROADMAP_PLANS = {
  30: {
    durationLabel: '30-Day Fast-Track Sprint',
    subtitle: 'High-impact closure of critical missing skills for immediate internship & entry-level readiness.',
    estimatedHours: 42,
    phases: [
      {
        id: '30-p1',
        timeframe: 'Days 1–10',
        title: 'Containerization & Environment Parity',
        skillFocus: 'Docker',
        priority: 'Critical',
        description: 'Containerize your FastAPI + React + PostgreSQL workflow with multi-stage Dockerfiles.',
        tasks: [
          { id: 't-30-1', title: 'Write production multi-stage Dockerfiles for backend & frontend', hours: 4, resource: 'Docker Official Docs' },
          { id: 't-30-2', title: 'Configure Docker Compose networking with PostgreSQL healthchecks', hours: 4, resource: 'Compose Networking Guide' },
          { id: 't-30-3', title: 'Practice image size optimization & .dockerignore hygiene', hours: 3, resource: 'Docker Best Practices' },
        ],
      },
      {
        id: '30-p2',
        timeframe: 'Days 11–20',
        title: 'Type-Safe Frontend Engineering',
        skillFocus: 'TypeScript',
        priority: 'Important',
        description: 'Upgrade React components and API contracts with strict TypeScript interfaces.',
        tasks: [
          { id: 't-30-4', title: 'Master TypeScript generics, utility types, and discriminated unions', hours: 5, resource: 'TypeScript Handbook' },
          { id: 't-30-5', title: 'Type Axios API clients and React hooks end-to-end', hours: 5, resource: 'React TypeScript Cheatsheet' },
          { id: 't-30-6', title: 'Convert a full dashboard feature module to strict TS mode', hours: 6, resource: 'Hands-on Capstone Lab' },
        ],
      },
      {
        id: '30-p3',
        timeframe: 'Days 21–30',
        title: 'Automated Testing & CI/CD Pipelines',
        skillFocus: 'CI/CD',
        priority: 'Important',
        description: 'Ship reliably with GitHub Actions, Pytest fixtures, and automated lint/build checks.',
        tasks: [
          { id: 't-30-7', title: 'Build a GitHub Actions workflow running pytest + Vite build on PRs', hours: 5, resource: 'GitHub Actions Docs' },
          { id: 't-30-8', title: 'Write integration tests for FastAPI routes using TestClient', hours: 5, resource: 'FastAPI Testing Guide' },
          { id: 't-30-9', title: 'Deploy containerized staging preview and verify health checks', hours: 5, resource: 'Deployment Checklist' },
        ],
      },
    ],
  },
  60: {
    durationLabel: '60-Day Career Accelerator',
    subtitle: 'Comprehensive full-stack + cloud architecture track with portfolio-ready production projects.',
    estimatedHours: 86,
    phases: [
      {
        id: '60-p1',
        timeframe: 'Days 1–15',
        title: 'Docker, Linux & Production Packaging',
        skillFocus: 'Docker',
        priority: 'Critical',
        description: 'Build repeatable containerized environments and local observability.',
        tasks: [
          { id: 't-60-1', title: 'Master Dockerfile caching layers and non-root container security', hours: 6, resource: 'Docker Security Guide' },
          { id: 't-60-2', title: 'Orchestrate multi-service Compose stacks with Alembic migrations', hours: 6, resource: 'Alembic + Compose Lab' },
          { id: 't-60-3', title: 'Configure structured JSON logging across services', hours: 5, resource: 'Observability Primer' },
        ],
      },
      {
        id: '60-p2',
        timeframe: 'Days 16–32',
        title: 'TypeScript & Modern React Patterns',
        skillFocus: 'TypeScript',
        priority: 'Critical',
        description: 'Eliminate runtime UI bugs with strict typing and reusable design-system patterns.',
        tasks: [
          { id: 't-60-4', title: 'Design strongly-typed component primitives and form schemas', hours: 8, resource: 'Total TypeScript Patterns' },
          { id: 't-60-5', title: 'Implement accessible keyboard navigation and ARIA landmarks', hours: 6, resource: 'WAI-ARIA Authoring Guide' },
          { id: 't-60-6', title: 'Add component & E2E smoke tests with Vitest/Playwright', hours: 8, resource: 'Playwright Docs' },
        ],
      },
      {
        id: '60-p3',
        timeframe: 'Days 33–48',
        title: 'Backend Performance, Caching & System Design',
        skillFocus: 'System Design',
        priority: 'Important',
        description: 'Scale PostgreSQL queries, add Redis caching, and design resilient APIs.',
        tasks: [
          { id: 't-60-7', title: 'Analyze PostgreSQL query plans with EXPLAIN ANALYZE and indexes', hours: 8, resource: 'Use The Index, Luke' },
          { id: 't-60-8', title: 'Implement Redis caching & rate-limiting middleware in FastAPI', hours: 8, resource: 'Redis Python Guide' },
          { id: 't-60-9', title: 'Document architecture trade-offs for 10k concurrent users', hours: 7, resource: 'System Design Primer' },
        ],
      },
      {
        id: '60-p4',
        timeframe: 'Days 49–60',
        title: 'CI/CD & Cloud Deployment Capstone',
        skillFocus: 'CI/CD',
        priority: 'Important',
        description: 'Automate testing, container builds, and zero-downtime cloud deployments.',
        tasks: [
          { id: 't-60-10', title: 'Set up automated CI pipeline with linting, pytest, and Docker build', hours: 8, resource: 'GitHub Actions Handbook' },
          { id: 't-60-11', title: 'Deploy live capstone with managed PostgreSQL and HTTPS', hours: 8, resource: 'Cloud Deploy Lab' },
          { id: 't-60-12', title: 'Update resume with quantified architecture metrics & live demo links', hours: 8, resource: 'Tech Resume Rubric' },
        ],
      },
    ],
  },
  90: {
    durationLabel: '90-Day Full-Stack + AI Mastery',
    subtitle: 'End-to-end engineering mastery spanning Full-Stack Systems, DevOps, and Applied AI/NLP integration.',
    estimatedHours: 132,
    phases: [
      {
        id: '90-p1',
        timeframe: 'Days 1–25',
        title: 'Foundational DevOps & TypeScript Engineering',
        skillFocus: 'Docker & TypeScript',
        priority: 'Critical',
        description: 'Solidify TypeScript, containerization, and automated test coverage.',
        tasks: [
          { id: 't-90-1', title: 'Complete TypeScript strict-mode migration and schema validation', hours: 12, resource: 'TypeScript Deep Dive' },
          { id: 't-90-2', title: 'Containerize full stack with healthchecks and environment secrets', hours: 10, resource: 'Docker Production Guide' },
          { id: 't-90-3', title: 'Achieve 80%+ automated test coverage on core API & UI flows', hours: 12, resource: 'Pytest + Playwright Suite' },
        ],
      },
      {
        id: '90-p2',
        timeframe: 'Days 26–55',
        title: 'Distributed Backend & Cloud Architecture',
        skillFocus: 'System Design',
        priority: 'Critical',
        description: 'Build scalable data pipelines, background queues, and cloud infrastructure.',
        tasks: [
          { id: 't-90-4', title: 'Implement asynchronous background job queues for resume parsing', hours: 14, resource: 'FastAPI Async Patterns' },
          { id: 't-90-5', title: 'Optimize PostgreSQL indexing, connection pooling, and migrations', hours: 12, resource: 'PostgreSQL Internals' },
          { id: 't-90-6', title: 'Provision cloud resources with Infrastructure as Code basics', hours: 12, resource: 'Cloud Architecture Lab' },
        ],
      },
      {
        id: '90-p3',
        timeframe: 'Days 56–78',
        title: 'Applied NLP & Semantic ML Services',
        skillFocus: 'NLP / Transformers',
        priority: 'Important',
        description: 'Integrate spaCy NER, Sentence Transformers, and Scikit-learn scoring into APIs.',
        tasks: [
          { id: 't-90-7', title: 'Build custom skill extraction pipeline with spaCy + NLTK', hours: 14, resource: 'spaCy Course' },
          { id: 't-90-8', title: 'Compute resume-to-role semantic similarity via Sentence Transformers', hours: 14, resource: 'SBERT Documentation' },
          { id: 't-90-9', title: 'Evaluate classifier precision/recall with cross-validation', hours: 10, resource: 'Scikit-learn User Guide' },
        ],
      },
      {
        id: '90-p4',
        timeframe: 'Days 79–90',
        title: 'Portfolio Launch & Technical Interview Readiness',
        skillFocus: 'Career Launch',
        priority: 'Important',
        description: 'Polish production deployment, architecture case studies, and mock interviews.',
        tasks: [
          { id: 't-90-10', title: 'Publish end-to-end architecture case study & interactive demo', hours: 10, resource: 'Engineering Portfolio Guide' },
          { id: 't-90-11', title: 'Complete 4 timed system design & coding mock interviews', hours: 12, resource: 'Interview Prep Rubric' },
        ],
      },
    ],
  },
};

export const INITIAL_COMPLETED_TASK_IDS = [
  't-30-1',
  't-30-2',
  't-30-4',
  't-60-1',
  't-60-2',
  't-90-1',
];

export const INITIAL_RECENT_ACTIVITY = [
  {
    id: 'act-1',
    type: 'resume',
    title: 'Resume analyzed: Alex_Rivera_CS_Resume_2026.pdf',
    detail: 'Extracted 12 verified technical skills across 5 domains',
    timestamp: '2 hours ago',
  },
  {
    id: 'act-2',
    type: 'roadmap',
    title: 'Completed milestone task: Docker Compose networking',
    detail: '30-Day Fast-Track Sprint progress reached 33%',
    timestamp: 'Yesterday',
  },
  {
    id: 'act-3',
    type: 'career',
    title: 'Evaluated career fit for Full-Stack Software Engineer',
    detail: '73% current compatibility · 3 priority skill gaps identified',
    timestamp: '2 days ago',
  },
  {
    id: 'act-4',
    type: 'job',
    title: 'Bookmarked Junior Full-Stack Engineer at Linearity Labs',
    detail: '86% skill match · Hybrid (San Francisco, CA)',
    timestamp: '3 days ago',
  },
];

/**
 * Compute compatibility metrics between a user's skill list and a target role or job.
 * Pure deterministic UI helper for demo mode (NOT an AI algorithm).
 */
export function computeSkillComparison(userSkills = [], requiredSkills = []) {
  const userSet = new Set(userSkills.map((s) => (typeof s === 'string' ? s : s.name).toLowerCase()));

  const normalizedRequired = requiredSkills.map((item) =>
    typeof item === 'string'
      ? { name: item, priority: 'Important', category: 'General' }
      : item,
  );

  const requiredSet = new Set(normalizedRequired.map((r) => r.name.toLowerCase()));

  const matched = normalizedRequired.filter((r) => userSet.has(r.name.toLowerCase()));
  const missing = normalizedRequired.filter((r) => !userSet.has(r.name.toLowerCase()));
  const additional = userSkills
    .map((s) => (typeof s === 'string' ? { name: s, category: 'General', level: 75 } : s))
    .filter((s) => !requiredSet.has(s.name.toLowerCase()));

  const score =
    normalizedRequired.length > 0
      ? Math.round((matched.length / normalizedRequired.length) * 100)
      : 0;

  return { score, matched, missing, additional };
}
