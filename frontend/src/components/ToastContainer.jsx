import { CheckCircle2, Info, X, AlertCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function ToastContainer() {
  const { toasts, dismissToast } = useApp();

  if (!toasts.length) return null;

  return (
    <div
      className="fixed right-5 bottom-5 z-50 flex max-w-sm flex-col gap-2.5"
      aria-live="polite"
    >
      {toasts.map((toast) => {
        const Icon =
          toast.type === 'error'
            ? AlertCircle
            : toast.type === 'info'
            ? Info
            : CheckCircle2;
        const accent =
          toast.type === 'error'
            ? 'border-rose-200 bg-white text-slate-900'
            : toast.type === 'info'
            ? 'border-indigo-200 bg-white text-slate-900'
            : 'border-emerald-200 bg-white text-slate-900';
        const iconColor =
          toast.type === 'error'
            ? 'text-rose-500'
            : toast.type === 'info'
            ? 'text-indigo-500'
            : 'text-emerald-500';

        return (
          <div
            key={toast.id}
            className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm shadow-lg transition-all ${accent}`}
          >
            <Icon className={`h-4 w-4 shrink-0 ${iconColor}`} />
            <span className="flex-1 font-medium">{toast.message}</span>
            <button
              type="button"
              onClick={() => dismissToast(toast.id)}
              className="rounded p-0.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              aria-label="Dismiss notification"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
