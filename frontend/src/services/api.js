import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';

const TOKEN_STORAGE_KEY = 'skillgap_access_token';

export function getAuthToken() {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  } catch {
    // Ignore storage issues
  }
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- Health APIs ---
export async function fetchBackendHealth() {
  const { data } = await apiClient.get('/api/health');
  return data;
}

export async function fetchDatabaseHealth() {
  try {
    const { data } = await apiClient.get('/api/health/db');
    return data;
  } catch (error) {
    if (error.response?.data) {
      return error.response.data;
    }
    throw error;
  }
}

// --- Auth APIs ---
export async function apiLogin(email, password) {
  const { data } = await apiClient.post('/api/auth/login', { email, password });
  setAuthToken(data.access_token);
  return data;
}

export async function apiRegister({ full_name, email, password }) {
  const { data } = await apiClient.post('/api/auth/register', {
    full_name,
    email,
    password,
  });
  setAuthToken(data.access_token);
  return data;
}

export async function apiGetMe() {
  const { data } = await apiClient.get('/api/auth/me');
  return data;
}

export async function apiUpdateProfile(fullName) {
  const { data } = await apiClient.patch('/api/auth/me', {
    full_name: fullName,
  });
  return data;
}

// --- Phase 8 Live Dashboard Analytics API ---
export async function fetchDashboardAnalytics() {
  const { data } = await apiClient.get('/api/dashboard/analytics');
  return data;
}

// --- Phase 4 Resume Analyzer & NLP Skill Extraction APIs ---
export async function uploadResumeFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post('/api/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function fetchResumeHistory() {
  const { data } = await apiClient.get('/api/resume/history');
  return data;
}

export async function fetchResumeDetail(resumeId) {
  const { data } = await apiClient.get(`/api/resume/${resumeId}`);
  return data;
}

export async function deleteResumeById(resumeId) {
  const { data } = await apiClient.delete(`/api/resume/${resumeId}`);
  return data;
}

export async function extractSkillsFromText(text) {
  const { data } = await apiClient.post('/api/skills/extract', { text });
  return data;
}

// --- Phase 5 Job Descriptions & Skill Gap Engine APIs ---
export async function fetchJobs(params = {}) {
  const { data } = await apiClient.get('/api/jobs', { params });
  return data;
}

export async function createJobDescription(payload) {
  const { data } = await apiClient.post('/api/jobs', payload);
  return data;
}

export async function fetchJobDetail(jobId) {
  const { data } = await apiClient.get(`/api/jobs/${jobId}`);
  return data;
}

export async function runSkillGapAnalysis(payload) {
  const { data } = await apiClient.post('/api/analysis/skill-gap', payload);
  return data;
}

export async function fetchAnalysisHistory() {
  const { data } = await apiClient.get('/api/analysis/history');
  return data;
}

export async function fetchAnalysisDetail(analysisId) {
  const { data } = await apiClient.get(`/api/analysis/${analysisId}`);
  return data;
}

// --- Phase 6 ML Career Prediction APIs ---
export async function predictCareerRoles(payload) {
  const { data } = await apiClient.post('/api/career/predict', payload);
  return data;
}

export async function fetchCareerRecommendations() {
  const { data } = await apiClient.get('/api/career/recommendations');
  return data;
}

// --- Phase 7 Personalized AI Learning Roadmap APIs ---
export async function generateRoadmap(payload) {
  const { data } = await apiClient.post('/api/roadmap/generate', payload);
  return data;
}

export async function fetchRoadmaps() {
  const { data } = await apiClient.get('/api/roadmap');
  return data;
}

export async function fetchRoadmapDetail(roadmapId) {
  const { data } = await apiClient.get(`/api/roadmap/${roadmapId}`);
  return data;
}

export async function updateRoadmapTask(taskId, isCompleted) {
  const { data } = await apiClient.patch(`/api/roadmap/tasks/${taskId}`, {
    is_completed: isCompleted,
  });
  return data;
}

export { API_BASE_URL, TOKEN_STORAGE_KEY };
