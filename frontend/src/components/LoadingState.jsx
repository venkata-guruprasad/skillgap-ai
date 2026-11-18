import { Loader2 } from 'lucide-react';

export default function LoadingState({ title = 'Loading...', subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200/80 bg-white px-6 py-14 text-center shadow-xs">
      <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      <p className="mt-3 text-sm font-semibold text-slate-900">{title}</p>
      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
}
