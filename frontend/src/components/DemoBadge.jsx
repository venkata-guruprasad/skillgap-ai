import { Database, Sparkles } from 'lucide-react';

export default function DemoBadge({ mode = 'demo', label }) {
  if (mode === 'live') {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-[11px] font-medium text-emerald-700">
        <Database className="h-3 w-3" />
        {label || 'Live API'}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-purple-200 bg-purple-50 px-2.5 py-0.5 text-[11px] font-medium text-purple-700">
      <Sparkles className="h-3 w-3" />
      {label || 'Demo Data'}
    </span>
  );
}
