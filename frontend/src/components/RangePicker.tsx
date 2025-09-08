type Props = { value: string; onChange: (v: string) => void };
const ranges = [
  { key: "90d", label: "90D" },
  { key: "180d", label: "6M" },
  { key: "365d", label: "1Y" },
  { key: "max", label: "MAX" },
];

export default function RangePicker({ value, onChange }: Props) {
  return (
    <div className="inline-flex rounded-lg overflow-hidden border border-slate-800">
      {ranges.map((r) => (
        <button
          key={r.key}
          onClick={() => onChange(r.key)}
          className={`px-3 py-1 text-xs ${value===r.key ? "bg-slate-800" : "bg-slate-900 hover:bg-slate-800/70"}`}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}
