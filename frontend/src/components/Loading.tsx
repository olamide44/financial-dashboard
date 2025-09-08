export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-slate-400 text-sm">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-transparent" />
      {label ?? "Loading…"}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-slate-800/70 rounded ${className}`} />;
}
