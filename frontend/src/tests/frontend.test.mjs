import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { CAREER_ROLES, computeSkillComparison } from '../data/demoData.js';
import { capitalize, formatTimestamp } from '../utils/formatters.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SRC_ROOT = path.resolve(__dirname, '..');

test('formatters handle valid, empty, and null inputs safely', () => {
  assert.equal(formatTimestamp(null), 'Never');
  const formatted = formatTimestamp(new Date('2026-05-01T10:15:30Z'));
  assert.equal(typeof formatted, 'string');
  assert.ok(formatted.length > 0);

  assert.equal(capitalize('python'), 'Python');
  assert.equal(capitalize(''), '');
});

test('computeSkillComparison computes exact matched, missing, and additional skills', () => {
  const userSkills = [
    { name: 'Python', category: 'Programming' },
    { name: 'SQL', category: 'Database' },
    { name: 'Docker', category: 'Cloud' },
  ];
  const required = ['Python', 'SQL', 'Machine Learning', 'Statistics'];
  const result = computeSkillComparison(userSkills, required);

  assert.equal(result.score, 50);
  assert.equal(result.matched.length, 2);
  assert.equal(result.missing.length, 2);
  assert.equal(result.additional.length, 1);
  assert.equal(result.additional[0].name, 'Docker');
});

test('all 11 required SaaS pages exist in src/pages', () => {
  const requiredPages = [
    'LandingPage.jsx',
    'LoginPage.jsx',
    'RegisterPage.jsx',
    'DashboardPage.jsx',
    'ResumeAnalyzerPage.jsx',
    'SkillGapPage.jsx',
    'CareerPredictionPage.jsx',
    'JobExplorerPage.jsx',
    'RoadmapPage.jsx',
    'ProgressPage.jsx',
    'ProfileSettingsPage.jsx',
  ];

  for (const fileName of requiredPages) {
    const fullPath = path.join(SRC_ROOT, 'pages', fileName);
    assert.ok(fs.existsSync(fullPath), `Missing page file: ${fileName}`);
    const content = fs.readFileSync(fullPath, 'utf-8');
    assert.ok(
      content.includes('export default function'),
      `Page ${fileName} must export a default React component`,
    );
  }
});

test('API client defines all Phase 1-8 backend endpoints', () => {
  const apiSource = fs.readFileSync(path.join(SRC_ROOT, 'services', 'api.js'), 'utf-8');
  const expectedEndpoints = [
    '/api/health',
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/me',
    '/api/dashboard/analytics',
    '/api/resume/upload',
    '/api/resume/history',
    '/api/skills/extract',
    '/api/jobs',
    '/api/analysis/skill-gap',
    '/api/analysis/history',
    '/api/career/predict',
    '/api/career/recommendations',
    '/api/roadmap/generate',
    '/api/roadmap',
    '/api/roadmap/tasks/',
  ];

  for (const endpoint of expectedEndpoints) {
    assert.ok(
      apiSource.includes(endpoint),
      `api.js is missing endpoint integration: ${endpoint}`,
    );
  }
});

test('no dead "#" links remain in JSX source files', () => {
  const jsxFiles = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name !== 'tests') walk(full);
      } else if (entry.name.endsWith('.jsx')) {
        jsxFiles.push(full);
      }
    }
  }
  walk(SRC_ROOT);
  assert.ok(jsxFiles.length >= 15);

  for (const file of jsxFiles) {
    const src = fs.readFileSync(file, 'utf-8');
    assert.equal(
      /href=["']#["']/.test(src),
      false,
      `Found dead '#' href in ${path.basename(file)}`,
    );
  }
});

test('CAREER_ROLES fallback metadata has non-empty requiredSkills', () => {
  assert.ok(CAREER_ROLES.length >= 5);
  for (const role of CAREER_ROLES) {
    assert.ok(role.title && role.requiredSkills.length >= 3);
  }
});
