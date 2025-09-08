import { subDays } from "date-fns";
import { useMemo, useState } from "react";
import toast from "react-hot-toast";
import { useParams } from "react-router-dom";
import PerformanceChart from "../components/charts/PerformanceChart";
import InsightsPanel from "../components/InsightsPanel";
import { Spinner } from "../components/Loading";
import RangePicker from "../components/RangePicker";
import { usePortfolioInsights } from "../hooks/useInsights";
import { usePortfolioPerformance } from "../hooks/usePortfolio";

export default function Portfolio() {
  const { id } = useParams();
  const [range, setRange] = useState<"90d"|"180d"|"365d"|"max">("365d");
  const [benchmark, setBenchmark] = useState<string>("SPY");
  const fromISO = useMemo(() => range==="max" ? undefined : subDays(new Date(), range==="90d"?90:range==="180d"?180:365).toISOString(), [range]);
  const { data, isLoading } = usePortfolioPerformance(id!, fromISO, benchmark);
  const insights = usePortfolioInsights();


  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Portfolio #{id}</h1>
        <div className="flex items-center gap-3">
          <RangePicker value={range} onChange={(v)=>setRange(v as any)} />
          <input
            value={benchmark}
            onChange={(e)=>setBenchmark(e.target.value.toUpperCase())}
            className="px-3 py-1.5 text-sm rounded bg-slate-800 border border-slate-700 w-28"
            placeholder="Benchmark"
          />
          <button
            className="px-3 py-1.5 text-sm rounded bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60"
            onClick={async () => {
              try {
                await insights.mutateAsync({ portfolioId: id!, fromISO, benchmark });
               toast.success("Insights generated");
              } catch (e: any) {
                toast.error(String(e?.response?.data?.detail ?? "Failed to generate insights"));
              }
            }}
            disabled={insights.isPending}
          >
            {insights.isPending ? "Thinking…" : "Generate Insights"}
          </button>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
        <h2 className="mb-2 font-medium">Performance</h2>
        {isLoading ? (
          <Spinner label="Loading performance…" />
        ) : (
          <PerformanceChart
            series={data?.series || []}
            benchmark={data?.benchmark?.series || []}
          />
        )}
      </div>

      {data?.metrics && (
        <div className="grid md:grid-cols-3 gap-3">
          {Object.entries(data.metrics).map(([k, v]) => (
            <div key={k} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="text-xs opacity-60">{k}</div>
              <div className="text-lg">{typeof v === "number" ? v.toFixed(3) : String(v ?? "-")}</div>
            </div>
          ))}
        </div>
      )}
      {insights.data?.insight ? <InsightsPanel text={insights.data.insight} /> : null}

    </div>
  );
}
