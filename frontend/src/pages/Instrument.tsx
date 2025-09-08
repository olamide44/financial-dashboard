import { subDays } from "date-fns";
import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { useParams } from "react-router-dom";
import { Skeleton, Spinner } from "../components/Loading";
import NewsList from "../components/NewsList";
import RangePicker from "../components/RangePicker";
import PriceChart from "../components/charts/PriceChart";
import SentimentChart from "../components/charts/SentimentChart";
import { useForecast, useStartForecast } from "../hooks/useForecast";
import { useIndicators } from "../hooks/useIndicators";
import { useNews } from "../hooks/useNews";
import { useCandles } from "../hooks/usePrices";
import { useSentiment } from "../hooks/useSentiment";
import { getJSON, setJSON } from "../lib/storage";

export default function Instrument() {
  const { id } = useParams();
  const instrumentId = Number(id);
  const [range, setRange] = useState<"90d"|"180d"|"365d"|"max">("180d");
  const [runId, setRunId] = useState<number | undefined>();


  const fromISO = useMemo(() => {
    const now = new Date();
    if (range === "max") return undefined;
    const days = range === "90d" ? 90 : range === "180d" ? 180 : 365;
    return subDays(now, days).toISOString();
  }, [range]);

    // load last runId for this instrument from storage
  useEffect(() => {
    const saved = getJSON<number>(`fc_run:${instrumentId}`);
    if (saved) setRunId(saved);
  }, [instrumentId]);

  const { data: candlesRes, isLoading: isCandles } = useCandles(instrumentId, fromISO);
  const candles = (candlesRes?.candles || []).map((c: any)=>({
    ts: c.ts, open: c.open, high: c.high, low: c.low, close: c.close, volume: c.volume,
  }));

    const { data: indRes, isLoading: isInd } = useIndicators(instrumentId, fromISO);
    const { data: sentRes, isLoading: isSent } = useSentiment(instrumentId, 14);
    const { data: fcRes, isLoading: isFc } = useForecast(runId);
    const startFc = useStartForecast();
    const { data: newsRes, isLoading: isNews } = useNews(instrumentId, 7);


  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Instrument #{instrumentId}</h1>
                <div className="flex items-center gap-3">
          <RangePicker value={range} onChange={(v)=>setRange(v as any)} />
          <button
            onClick={async () => {
              try {
                const res = await startFc.mutateAsync({ instrumentId, horizon: 7, lookback: 365, model: "ridge" });
                setRunId(res.run_id);
                setJSON(`fc_run:${instrumentId}`, res.run_id);
                toast.success("Forecast ready");

              } catch (e: any) {
                toast.error(String(e?.response?.data?.detail ?? "Forecast failed"));
              }
            }}
            className="px-3 py-1.5 text-sm rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-60"
            disabled={startFc.isPending}
          >
            {startFc.isPending ? "Forecasting…" : "Forecast 7d"}
          </button>
        </div>
      </div>
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
        {(isCandles || isInd) && <Spinner label="Loading chart data…" />}
        {!isCandles && !isInd && (
          <PriceChart
            candles={candles}
            indicators={indRes?.indicators}
            forecast={fcRes ? { points: fcRes.points } : undefined}
            title="Price & Indicators"
          />
        )}
      </div>
      {isSent && <Skeleton className="h-36" />}
      {!isSent && sentRes?.daily?.length ? (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <h2 className="mb-3 font-medium">News Sentiment (14d)</h2>
          <SentimentChart daily={sentRes.daily} />
        </div>
      ) : null}
     <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
        <h2 className="mb-3 font-medium">Latest News</h2>
        {isNews ? <Skeleton className="h-24" /> : <NewsList articles={newsRes?.articles || []} />}
      </div>

    </div>
  );
}
