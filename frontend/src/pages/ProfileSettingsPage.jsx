import { useEffect, useState } from 'react';
import {
  Bell,
  Layers,
  Plus,
  RotateCcw,
  Save,
  Target,
  User,
  X,
} from 'lucide-react';
import DemoBadge from '../components/DemoBadge';
import { useApp } from '../context/AppContext';
import { CAREER_ROLES } from '../data/demoData';

const TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'career', label: 'Career Preferences', icon: Target },
  { id: 'skills', label: 'Skills Profile', icon: Layers },
  { id: 'notifications', label: 'Notifications & Data', icon: Bell },
];

export default function ProfileSettingsPage() {
  const {
    authToken,
    user,
    updateProfile,
    userSkills,
    addUserSkill,
    removeUserSkill,
    resetDemoData,
  } = useApp();

  const [activeTab, setActiveTab] = useState('profile');
  const [formState, setFormState] = useState({
    fullName: user.fullName,
    email: user.email,
    headline: user.headline,
    university: user.university,
    graduationYear: user.graduationYear,
    targetRoleId: user.targetRoleId,
    weeklyGoalHours: user.weeklyGoalHours,
    bio: user.bio,
    notifications: { ...user.notifications },
  });

  useEffect(() => {
    setFormState({
      fullName: user.fullName,
      email: user.email,
      headline: user.headline,
      university: user.university,
      graduationYear: user.graduationYear,
      targetRoleId: user.targetRoleId,
      weeklyGoalHours: user.weeklyGoalHours,
      bio: user.bio,
      notifications: { ...user.notifications },
    });
  }, [user]);

  const [newSkill, setNewSkill] = useState('');
  const [newCategory, setNewCategory] = useState('Backend');

  const handleSave = (e) => {
    e.preventDefault();
    updateProfile({
      ...formState,
      weeklyGoalHours: Number(formState.weeklyGoalHours) || 10,
    });
  };

  const handleToggleNotification = (key) => {
    const updatedNotifications = {
      ...formState.notifications,
      [key]: !formState.notifications[key],
    };
    setFormState((prev) => ({ ...prev, notifications: updatedNotifications }));
    updateProfile({ notifications: updatedNotifications });
  };

  const handleAddSkill = (e) => {
    e.preventDefault();
    if (addUserSkill(newSkill, newCategory, 78)) {
      setNewSkill('');
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Settings Sidebar Tabs */}
        <aside className="rounded-2xl border border-slate-200/80 bg-white p-3 shadow-xs lg:col-span-3 lg:self-start">
          <div className="mb-2 flex items-center justify-between px-3 py-1.5">
            <span className="text-xs font-semibold text-slate-500 uppercase">
              Settings
            </span>
            <DemoBadge
              mode={authToken ? 'live' : 'demo'}
              label={authToken ? 'Live Profile API' : 'Local State'}
            />
          </div>
          <nav className="space-y-1">
            {TABS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveTab(id)}
                className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-left text-xs font-semibold transition ${
                  activeTab === id
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* Settings Content Panel */}
        <section className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs lg:col-span-9">
          {activeTab === 'profile' && (
            <form onSubmit={handleSave} className="space-y-5">
              <div>
                <h2 className="text-base font-bold text-slate-950">
                  Student Profile Information
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  Update your name, academic background, and short career bio.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={formState.fullName}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, fullName: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={formState.email}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, email: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    Academic Headline
                  </label>
                  <input
                    type="text"
                    value={formState.headline}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, headline: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    University / Institution
                  </label>
                  <input
                    type="text"
                    value={formState.university}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, university: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Short Career Bio
                </label>
                <textarea
                  rows={3}
                  value={formState.bio}
                  onChange={(e) =>
                    setFormState((p) => ({ ...p, bio: e.target.value }))
                  }
                  className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end border-t border-slate-100 pt-4">
                <button
                  type="submit"
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700"
                >
                  <Save className="h-3.5 w-3.5" />
                  <span>Save Changes</span>
                </button>
              </div>
            </form>
          )}

          {activeTab === 'career' && (
            <form onSubmit={handleSave} className="space-y-5">
              <div>
                <h2 className="text-base font-bold text-slate-950">
                  Career &amp; Study Preferences
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  Your primary target role drives Dashboard compatibility cards and Skill
                  Gap defaults.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    Primary Target Career Role
                  </label>
                  <select
                    value={formState.targetRoleId}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, targetRoleId: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                  >
                    {CAREER_ROLES.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.title} ({role.avgSalary})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    Weekly Study Goal (Hours)
                  </label>
                  <input
                    type="number"
                    min={2}
                    max={45}
                    value={formState.weeklyGoalHours}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, weeklyGoalHours: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700">
                    Expected Graduation Year
                  </label>
                  <input
                    type="text"
                    value={formState.graduationYear}
                    onChange={(e) =>
                      setFormState((p) => ({ ...p, graduationYear: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex justify-end border-t border-slate-100 pt-4">
                <button
                  type="submit"
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700"
                >
                  <Save className="h-3.5 w-3.5" />
                  <span>Save Preferences</span>
                </button>
              </div>
            </form>
          )}

          {activeTab === 'skills' && (
            <div className="space-y-5">
              <div>
                <h2 className="text-base font-bold text-slate-950">
                  Verified Skills Profile ({userSkills.length})
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  Add or remove skills here to immediately recalculate compatibility across
                  Dashboard, Career Prediction, Skill Gaps, and Job Explorer.
                </p>
              </div>

              <form onSubmit={handleAddSkill} className="flex flex-col gap-2.5 sm:flex-row">
                <input
                  type="text"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  placeholder="Enter a skill (e.g., Docker, TypeScript, Redis, PyTorch)"
                  className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                />
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-800 focus:border-indigo-500 focus:outline-none"
                >
                  <option value="Frontend">Frontend</option>
                  <option value="Backend">Backend</option>
                  <option value="Database">Database</option>
                  <option value="Data & AI">Data &amp; AI</option>
                  <option value="Tools & DevOps">Tools &amp; DevOps</option>
                </select>
                <button
                  type="submit"
                  className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Skill</span>
                </button>
              </form>

              <div className="flex flex-wrap gap-2">
                {userSkills.map((skill) => (
                  <span
                    key={skill.name}
                    className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-800"
                  >
                    <span>{skill.name}</span>
                    <span className="text-[10px] text-slate-500">{skill.category}</span>
                    <button
                      type="button"
                      onClick={() => removeUserSkill(skill.name)}
                      className="rounded p-0.5 text-slate-400 hover:bg-slate-200 hover:text-rose-600"
                      aria-label={`Remove ${skill.name}`}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-base font-bold text-slate-950">
                  Notifications &amp; Demo Workspace Controls
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  Manage email alert preferences or reset local demo state.
                </p>
              </div>

              <div className="divide-y divide-slate-100 rounded-xl border border-slate-200/80">
                {[
                  {
                    key: 'weeklyDigest',
                    title: 'Weekly Readiness Digest',
                    desc: 'Receive a summary of weekly study hours and rising career fit scores.',
                  },
                  {
                    key: 'jobAlerts',
                    title: 'High-Compatibility Job Alerts',
                    desc: 'Notify when new internships or roles exceed 75% skill match.',
                  },
                  {
                    key: 'roadmapReminders',
                    title: 'Learning Roadmap Reminders',
                    desc: 'Gentle nudges to stay on pace with your 30/60/90-day milestones.',
                  },
                  {
                    key: 'productUpdates',
                    title: 'Platform & AI Engine Updates',
                    desc: 'Announcements when new NLP, ML, and roadmap capabilities release.',
                  },
                ].map((item) => {
                  const enabled = Boolean(formState.notifications[item.key]);
                  return (
                    <div
                      key={item.key}
                      className="flex items-center justify-between gap-4 p-4"
                    >
                      <div>
                        <p className="text-xs font-semibold text-slate-900">
                          {item.title}
                        </p>
                        <p className="mt-0.5 text-xs text-slate-500">{item.desc}</p>
                      </div>
                      <button
                        type="button"
                        role="switch"
                        aria-checked={enabled}
                        onClick={() => handleToggleNotification(item.key)}
                        className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${
                          enabled ? 'bg-indigo-600' : 'bg-slate-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 translate-y-0.5 rounded-full bg-white shadow-xs transition-transform ${
                            enabled ? 'translate-x-4.5' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                  );
                })}
              </div>

              <div className="flex flex-col justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center">
                <div>
                  <p className="text-xs font-semibold text-slate-900">
                    Reset Demo Workspace Data
                  </p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    Restores default demo skills, resume summary, roadmap tasks, and study
                    logs.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={resetDemoData}
                  className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:border-rose-300 hover:text-rose-700"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span>Reset Defaults</span>
                </button>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
