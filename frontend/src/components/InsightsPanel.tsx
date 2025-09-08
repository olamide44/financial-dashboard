export default function InsightsPanel({ text }: { text: string }) {
  if (!text) return null;
  // Keep simple: render markdown-ish bullets if present
  const lines = text.split("\n").filter(Boolean);
  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
      <h2 className="mb-3 font-medium">AI Insights</h2>
      <ul className="list-disc list-inside space-y-1 text-sm">
        {lines.map((l, i) => (
          <li key={i}>{l.replace(/^\-\s*/, "")}</li>
        ))}
      </ul>
    </div>
  );
}
