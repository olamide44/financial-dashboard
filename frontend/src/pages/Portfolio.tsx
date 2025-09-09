import { subDays } from "date-fns";
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import PerformanceChart from "../components/charts/PerformanceChart";
import HoldingsImport from "../components/HoldingsImport";
import HoldingsTable from "../components/HoldingsTable";
import InsightsPanel from "../components/InsightsPanel";
import { Spinner } from "../components/Loading";
import RangePicker from "../components/RangePicker";
import TransactionForm from "../components/TransactionForm";
import { usePortfolioHoldings } from "../hooks/useHoldings";
import { usePortfolioInsights } from "../hooks/useInsights";
import { usePortfolioPerformance } from "../hooks/usePortfolio";

export default function Portfolio() {
  const { id } = useParams();
  const [range, setRange] = useState<"90d" | "180d" | "365d" | "max">("365d");
  const [benchmark, setBenchmark] = useState<string>("SPY");
  const fromISO = useMemo(
    () =>
      range === "max"
        ? undefined
        : subDays(
            new Date(),
            range === "90d" ? 90 : range === "180d" ? 180 : 365
          ).toISOString(),
    [range]
  );
  const { data, isLoading } = usePortfolioPerformance(id!, fromISO, benchmark);
  const insights = usePortfolioInsights();
  const { data: holds, isLoading: isHoldLoading } = usePortfolioHoldings(id!);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            Portfolio #{id}
          </h1>
          <p className="text-sm text-text-muted">
            Performance, holdings, insights
          </p>
        </div>{" "}
        <div className="flex items-center gap-3">
          <RangePicker value={range} onChange={(v) => setRange(v as any)} />
          <input
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value.toUpperCase())}
            className="px-3 py-1.5 text-sm rounded bg-slate-800 border border-slate-700 w-28"
            placeholder="Benchmark"
          />
          <button className="btn h-10">Generate Insights</button>
        </div>
      </div>

      <div className="card p-4">
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
            <div key={k} className="card p-3">
              <div className="text-xs opacity-60">{k}</div>
              <div className="text-lg">
                {typeof v === "number" ? v.toFixed(3) : String(v ?? "-")}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="card p-4">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="font-medium">Holdings</h2>
          <HoldingsImport portfolioId={id!} />
        </div>
        {isHoldLoading ? (
          <Spinner label="Loading holdings…" />
        ) : (
          <HoldingsTable rows={holds || []} />
        )}
      </div>
      <TransactionForm portfolioId={id!} />

      {insights.data?.insight ? (
        <div className="card">
          <InsightsPanel text={insights.data.insight} />
        </div>
      ) : null}
    </div>
  );
}
