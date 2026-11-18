export default function MetricCard({
  title,
  value,
  subtitle,
  badge,
  icon: Icon,
  accent = 'indigo',
  onClick,
}) {
  const accentMap = {
    indigo: 'bg-indigo-50 text-indigo-600 ring-indigo-100',
    blue: 'bg-blue-50 text-blue-600 ring-blue-100',
    purple: 'bg-purple-50 text-purple-600 ring-purple-100',
    emerald: 'bg-emerald-50 text-emerald-600 ring-emerald-100',
    rose: 'bg-rose-50 text-rose-600 ring-rose-100',
    amber: 'bg-amber-50 text-amber-600 ring-amber-100',
  };

  const Component = onClick ? 'button' : 'div';

  return (
    <Component
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      className={`w-full rounded-xl border border-slate-200/80 bg-white p-5 text-left shadow-[0_1px_2px_rgba(15,23,42,0.04)] transition-all ${
        onClick ? 'hover:border-indigo-200 hover:shadow-sm' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-slate-500">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums">
              {value}
            </span>
            {badge && (
              <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[11px] font-medium text-slate-600">
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="mt-1.5 truncate text-xs text-slate-500">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ring-1 ${
              accentMap[accent] || accentMap.indigo
            }`}
          >
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>
    </Component>
  );
}
