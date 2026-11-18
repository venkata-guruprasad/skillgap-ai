import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  CAREER_ROLES,
  DEFAULT_USER,
  INITIAL_COMPLETED_TASK_IDS,
  INITIAL_RECENT_ACTIVITY,
  INITIAL_RESUME_SUMMARY,
  INITIAL_USER_SKILLS,
  ROADMAP_PLANS,
  WEEKLY_LEARNING_DATA,
  computeSkillComparison,
} from '../data/demoData';
import { useBackendHealth } from '../hooks/useBackendHealth';
import {
  apiGetMe,
  apiLogin,
  apiRegister,
  apiUpdateProfile,
  fetchAnalysisDetail,
  fetchAnalysisHistory,
  fetchDashboardAnalytics,
  fetchRoadmapDetail,
  fetchRoadmaps,
  getAuthToken,
  setAuthToken,
} from '../services/api';

const STORAGE_KEY = 'skillgap_ai_state_v2';

function loadStoredState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const stored = useMemo(() => loadStoredState(), []);
  const health = useBackendHealth();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [authToken, setAuthTokenState] = useState(() => getAuthToken());
  const [isAuthenticated, setIsAuthenticated] = useState(
    Boolean(getAuthToken()) || (stored?.isAuthenticated ?? true),
  );
  const [user, setUser] = useState(stored?.user ?? DEFAULT_USER);
  const [userSkills, setUserSkills] = useState(
    stored?.userSkills ?? INITIAL_USER_SKILLS,
  );
  const [resumeSummary, setResumeSummary] = useState(
    stored?.resumeSummary ?? INITIAL_RESUME_SUMMARY,
  );
  const [activeResumeDetail, setActiveResumeDetail] = useState(null);
  const [latestSkillGapAnalysis, setLatestSkillGapAnalysis] = useState(null);
  const [liveRoadmap, setLiveRoadmap] = useState(null);
  const [dashboardAnalytics, setDashboardAnalytics] = useState(null);
  const [roadmapHorizon, setRoadmapHorizon] = useState(
    stored?.roadmapHorizon ?? 30,
  );
  const [completedTaskIds, setCompletedTaskIds] = useState(
    stored?.completedTaskIds ?? INITIAL_COMPLETED_TASK_IDS,
  );
  const [customTasksByPhase, setCustomTasksByPhase] = useState(
    stored?.customTasksByPhase ?? {},
  );
  const [savedJobIds, setSavedJobIds] = useState(
    stored?.savedJobIds ?? ['job-1', 'job-2'],
  );
  const [appliedJobIds, setAppliedJobIds] = useState(
    stored?.appliedJobIds ?? [],
  );
  const [weeklyData, setWeeklyData] = useState(
    stored?.weeklyData ?? WEEKLY_LEARNING_DATA,
  );
  const [recentActivity, setRecentActivity] = useState(
    stored?.recentActivity ?? INITIAL_RECENT_ACTIVITY,
  );
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          isAuthenticated,
          user,
          userSkills,
          resumeSummary,
          roadmapHorizon,
          completedTaskIds,
          customTasksByPhase,
          savedJobIds,
          appliedJobIds,
          weeklyData,
          recentActivity,
        }),
      );
    } catch {
      // Ignore storage quota issues
    }
  }, [
    isAuthenticated,
    user,
    userSkills,
    resumeSummary,
    roadmapHorizon,
    completedTaskIds,
    customTasksByPhase,
    savedJobIds,
    appliedJobIds,
    weeklyData,
    recentActivity,
  ]);

  // Verify existing JWT token against backend on initial load if present
  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;
    apiGetMe()
      .then((me) => {
        setIsAuthenticated(true);
        setAuthTokenState(token);
        setUser((prev) => ({
          ...prev,
          id: me.id,
          fullName: me.full_name,
          email: me.email,
        }));
      })
      .catch(() => {
        setAuthToken(null);
        setAuthTokenState(null);
      });
  }, []);

  const refreshDashboardAnalytics = useCallback(async () => {
    if (!getAuthToken()) return null;
    try {
      const data = await fetchDashboardAnalytics();
      setDashboardAnalytics(data);
      return data;
    } catch {
      return null;
    }
  }, []);

  // Load latest persisted backend skill gap analysis, active roadmap & dashboard analytics when authenticated
  useEffect(() => {
    if (!authToken) {
      setLatestSkillGapAnalysis(null);
      setLiveRoadmap(null);
      setDashboardAnalytics(null);
      return;
    }
    fetchAnalysisHistory()
      .then((hist) => {
        if (hist?.items?.length > 0) {
          return fetchAnalysisDetail(hist.items[0].id).then((detail) => {
            setLatestSkillGapAnalysis(detail);
          });
        }
        setLatestSkillGapAnalysis(null);
        return null;
      })
      .catch(() => {
        // Keep dashboard graceful if no analysis exists yet
      });

    fetchRoadmaps()
      .then((list) => {
        if (list?.active_roadmap_id) {
          return fetchRoadmapDetail(list.active_roadmap_id).then((rm) => {
            setLiveRoadmap(rm);
          });
        }
        setLiveRoadmap(null);
        return null;
      })
      .catch(() => {
        // Keep roadmap graceful if none generated yet
      });

    refreshDashboardAnalytics();
  }, [authToken, refreshDashboardAnalytics]);

  const notify = useCallback((message, type = 'success') => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3800);
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const pushActivity = useCallback((type, title, detail) => {
    setRecentActivity((prev) => [
      {
        id: `act-${Date.now()}`,
        type,
        title,
        detail,
        timestamp: 'Just now',
      },
      ...prev.slice(0, 11),
    ]);
  }, []);

  const login = useCallback(
    async (email, password = 'demo-password-2026') => {
      const data = await apiLogin(email, password);
      setAuthTokenState(data.access_token);
      setIsAuthenticated(true);
      setUser((prev) => ({
        ...prev,
        id: data.user.id,
        fullName: data.user.full_name,
        email: data.user.email,
      }));
      notify(`Signed in as ${data.user.full_name}`);
      return data;
    },
    [notify],
  );

  const register = useCallback(
    async ({ fullName, email, password, targetRoleId }) => {
      const data = await apiRegister({
        full_name: fullName,
        email,
        password,
      });
      setAuthTokenState(data.access_token);
      setIsAuthenticated(true);
      setActiveResumeDetail(null);
      setResumeSummary(null);
      setLatestSkillGapAnalysis(null);
      setLiveRoadmap(null);
      setDashboardAnalytics(null);
      setUser((prev) => ({
        ...prev,
        id: data.user.id,
        fullName: data.user.full_name,
        email: data.user.email,
        targetRoleId: targetRoleId || prev.targetRoleId,
      }));
      pushActivity('profile', `Account created for ${data.user.full_name}`, 'Authenticated with SkillGap AI backend');
      notify(`Welcome to SkillGap AI, ${data.user.full_name}!`);
      return data;
    },
    [notify, pushActivity],
  );

  const logout = useCallback(() => {
    setAuthToken(null);
    setAuthTokenState(null);
    setActiveResumeDetail(null);
    setLatestSkillGapAnalysis(null);
    setLiveRoadmap(null);
    setDashboardAnalytics(null);
    setIsAuthenticated(false);
    notify('You have been signed out', 'info');
  }, [notify]);

  const updateProfile = useCallback(
    async (updates) => {
      setUser((prev) => ({ ...prev, ...updates }));
      if (getAuthToken() && updates.fullName && updates.fullName.trim().length >= 2) {
        try {
          const updated = await apiUpdateProfile(updates.fullName.trim());
          setUser((prev) => ({ ...prev, fullName: updated.full_name }));
        } catch {
          // Keep optimistic local update even if offline
        }
      }
      pushActivity('profile', 'Updated profile settings', 'Saved career preferences and account details');
      notify('Profile settings saved');
    },
    [notify, pushActivity],
  );

  const setTargetRoleId = useCallback(
    (roleId) => {
      const role = CAREER_ROLES.find((r) => r.id === roleId);
      setUser((prev) => ({ ...prev, targetRoleId: roleId }));
      if (role) {
        pushActivity('career', `Target role set to ${role.title}`, `${role.category} · ${role.avgSalary} avg`);
        notify(`Target role updated to ${role.title}`);
      }
    },
    [notify, pushActivity],
  );

  const addUserSkill = useCallback(
    (name, category = 'General', level = 75) => {
      const trimmed = name.trim();
      if (!trimmed) return false;
      const exists = userSkills.some(
        (s) => s.name.toLowerCase() === trimmed.toLowerCase(),
      );
      if (exists) {
        notify(`"${trimmed}" is already in your skill profile`, 'info');
        return false;
      }
      setUserSkills((prev) => [
        ...prev,
        { name: trimmed, category, level, confidence: 1.0 },
      ]);
      pushActivity('resume', `Added skill: ${trimmed}`, `Category: ${category}`);
      notify(`Added "${trimmed}" to your skills`);
      return true;
    },
    [userSkills, notify, pushActivity],
  );

  const removeUserSkill = useCallback(
    (name) => {
      setUserSkills((prev) =>
        prev.filter((s) => s.name.toLowerCase() !== name.toLowerCase()),
      );
      notify(`Removed "${name}" from your skills`, 'info');
    },
    [notify],
  );

  /**
   * Sync live NLP resume analysis results returned by POST /api/resume/upload or GET /api/resume/{id}
   * into the global workspace (Dashboard, Skill Gaps, Career Prediction, Job Explorer).
   */
  const syncLiveResumeAnalysis = useCallback(
    (resumeDetail) => {
      if (!resumeDetail) return;
      setActiveResumeDetail(resumeDetail);
      const analysis = resumeDetail.analysis || {};
      const summary = analysis.summary || {};

      setResumeSummary({
        id: resumeDetail.id,
        fileName: resumeDetail.file_name,
        fileSizeKb: Math.max(1, Math.round((resumeDetail.file_size_bytes || 0) / 1024)),
        fileType: resumeDetail.file_type,
        analyzedAt: resumeDetail.created_at,
        atsScore: summary.ats_score ?? 0,
        wordCount: summary.word_count ?? 0,
        sectionsDetected: summary.sections_detected || [],
        suggestions: summary.recommendations || [],
        isLive: true,
      });

      const extractedTech = analysis.technical_skills || [];
      if (extractedTech.length > 0) {
        setUserSkills(
          extractedTech.map((s) => ({
            name: s.name,
            category: s.category,
            level: Math.round((s.confidence || 0.8) * 100),
            confidence: s.confidence || 0.8,
            evidence: s.evidence || [],
          })),
        );
      }

      pushActivity(
        'resume',
        `Analyzed resume: ${resumeDetail.file_name}`,
        `Extracted ${extractedTech.length} technical skills & ${(analysis.soft_skills || []).length} soft skills (Live NLP)`,
      );
    },
    [pushActivity],
  );

  const clearResume = useCallback(() => {
    setActiveResumeDetail(null);
    setResumeSummary(null);
    notify('Cleared active resume selection', 'info');
  }, [notify]);

  const toggleRoadmapTask = useCallback(
    (taskId, taskTitle) => {
      setCompletedTaskIds((prev) => {
        const isDone = prev.includes(taskId);
        const next = isDone ? prev.filter((id) => id !== taskId) : [...prev, taskId];
        if (!isDone && taskTitle) {
          pushActivity('roadmap', `Completed task: ${taskTitle}`, 'Learning roadmap progress updated');
        }
        return next;
      });
    },
    [pushActivity],
  );

  const addCustomRoadmapTask = useCallback(
    (phaseId, title, hours = 3) => {
      const trimmed = title.trim();
      if (!trimmed) return;
      const newTask = {
        id: `custom-${Date.now()}`,
        title: trimmed,
        hours: Number(hours) || 3,
        resource: 'Custom Study Goal',
        isCustom: true,
      };
      setCustomTasksByPhase((prev) => ({
        ...prev,
        [phaseId]: [...(prev[phaseId] || []), newTask],
      }));
      pushActivity('roadmap', `Added roadmap task: ${trimmed}`, `Estimated ${newTask.hours} hrs`);
      notify('Custom learning task added');
    },
    [notify, pushActivity],
  );

  const toggleSaveJob = useCallback(
    (job) => {
      setSavedJobIds((prev) => {
        const exists = prev.includes(job.id);
        notify(
          exists ? `Removed "${job.title}" from saved jobs` : `Saved "${job.title}"`,
          exists ? 'info' : 'success',
        );
        if (!exists) {
          pushActivity('job', `Saved role: ${job.title}`, `${job.company} · ${job.location}`);
        }
        return exists ? prev.filter((id) => id !== job.id) : [...prev, job.id];
      });
    },
    [notify, pushActivity],
  );

  const applyToJob = useCallback(
    (job) => {
      if (appliedJobIds.includes(job.id)) {
        notify(`You already applied to ${job.title}`, 'info');
        return;
      }
      setAppliedJobIds((prev) => [...prev, job.id]);
      pushActivity('job', `Applied to ${job.title}`, `${job.company} · Demo application tracked`);
      notify(`Application tracked for ${job.title} at ${job.company}`);
    },
    [appliedJobIds, notify, pushActivity],
  );

  const logStudySession = useCallback(
    (hours, topic) => {
      const hrs = Number(hours);
      if (!hrs || hrs <= 0) return;
      setWeeklyData((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        updated[lastIdx] = {
          ...updated[lastIdx],
          hours: Number((updated[lastIdx].hours + hrs).toFixed(1)),
          tasksCompleted: updated[lastIdx].tasksCompleted + 1,
          readiness: Math.min(100, updated[lastIdx].readiness + 1),
        };
        return updated;
      });
      pushActivity('roadmap', `Logged ${hrs}h study session`, topic || 'Focused skill practice');
      notify(`Logged ${hrs} hours of study progress`);
    },
    [notify, pushActivity],
  );

  const resetDemoData = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(DEFAULT_USER);
    setUserSkills(INITIAL_USER_SKILLS);
    setResumeSummary(INITIAL_RESUME_SUMMARY);
    setActiveResumeDetail(null);
    setRoadmapHorizon(30);
    setCompletedTaskIds(INITIAL_COMPLETED_TASK_IDS);
    setCustomTasksByPhase({});
    setSavedJobIds(['job-1', 'job-2']);
    setAppliedJobIds([]);
    setWeeklyData(WEEKLY_LEARNING_DATA);
    setRecentActivity(INITIAL_RECENT_ACTIVITY);
    notify('Demo workspace restored to initial defaults', 'info');
  }, [notify]);

  const targetRole = useMemo(
    () => CAREER_ROLES.find((r) => r.id === user.targetRoleId) || CAREER_ROLES[0],
    [user.targetRoleId],
  );

  const targetRoleComparison = useMemo(
    () => computeSkillComparison(userSkills, targetRole.requiredSkills),
    [userSkills, targetRole],
  );

  const careerPredictions = useMemo(() => {
    return CAREER_ROLES.map((role) => {
      const cmp = computeSkillComparison(userSkills, role.requiredSkills);
      return {
        ...role,
        compatibility: cmp.score,
        matchedSkills: cmp.matched,
        missingSkills: cmp.missing,
        additionalSkills: cmp.additional,
      };
    }).sort((a, b) => b.compatibility - a.compatibility);
  }, [userSkills]);

  const activeRoadmapStats = useMemo(() => {
    if (liveRoadmap?.progress) {
      const p = liveRoadmap.progress;
      const flatTasks = (liveRoadmap.phases || []).flatMap((ph) =>
        (ph.tasks || []).map((t) => ({
          ...t,
          hours: t.estimated_hours,
          resource: `Phase ${ph.phase_number} · ${t.skill_name} · ${t.week_label}`,
          isLive: true,
        })),
      );
      return {
        isLive: true,
        durationDays: liveRoadmap.duration_days,
        targetRole: liveRoadmap.target_role,
        completedCount: p.completed_tasks,
        totalCount: p.total_tasks,
        percent: Math.round(p.progress_percent),
        remainingHours: p.remaining_hours,
        allTasks: flatTasks,
      };
    }
    const plan = ROADMAP_PLANS[roadmapHorizon] || ROADMAP_PLANS[30];
    const allTasks = plan.phases.flatMap((phase) => [
      ...phase.tasks,
      ...(customTasksByPhase[phase.id] || []),
    ]);
    const completedCount = allTasks.filter((t) => completedTaskIds.includes(t.id)).length;
    const totalCount = allTasks.length;
    const percent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
    const remainingHours = allTasks
      .filter((t) => !completedTaskIds.includes(t.id))
      .reduce((acc, t) => acc + (t.hours || 0), 0);
    return {
      isLive: false,
      durationDays: roadmapHorizon,
      targetRole: targetRole.title,
      completedCount,
      totalCount,
      percent,
      remainingHours,
      allTasks,
    };
  }, [liveRoadmap, roadmapHorizon, customTasksByPhase, completedTaskIds, targetRole.title]);

  return (
    <AppContext.Provider
      value={{
        appName: import.meta.env.VITE_APP_NAME || 'SkillGap AI',
        sidebarOpen,
        setSidebarOpen,
        toggleSidebar: () => setSidebarOpen((prev) => !prev),
        health,
        authToken,
        isAuthenticated,
        user,
        login,
        register,
        logout,
        updateProfile,
        setTargetRoleId,
        userSkills,
        addUserSkill,
        removeUserSkill,
        resumeSummary,
        activeResumeDetail,
        latestSkillGapAnalysis,
        setLatestSkillGapAnalysis,
        liveRoadmap,
        setLiveRoadmap,
        dashboardAnalytics,
        refreshDashboardAnalytics,
        syncLiveResumeAnalysis,
        clearResume,
        roadmapHorizon,
        setRoadmapHorizon,
        completedTaskIds,
        customTasksByPhase,
        toggleRoadmapTask,
        addCustomRoadmapTask,
        activeRoadmapStats,
        savedJobIds,
        appliedJobIds,
        toggleSaveJob,
        applyToJob,
        weeklyData,
        logStudySession,
        recentActivity,
        targetRole,
        targetRoleComparison,
        careerPredictions,
        toasts,
        notify,
        dismissToast,
        resetDemoData,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return ctx;
}
