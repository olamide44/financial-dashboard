import { subDays } from "date-fns";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Skeleton, Spinner } from "../components/Loading";
import NewsList from "../components/NewsList";
import RangePicker from "../components/RangePicker";
import PriceChart from "../components/charts/PriceChart";
import SentimentChart from "../components/charts/SentimentChart";
import { useForecast, useStartForecast } from "../hooks/useForecast";
import { useIndicators } from "../hooks/useIndicators";
import { useInstrument } from "../hooks/useInstruments";
import { useNews } from "../hooks/useNews";
import { useCandles } from "../hooks/usePrices";
import { useSentiment } from "../hooks/useSentiment";
import { useSyncPrices } from "../hooks/useSyncPrices";
import { pushRecentInstrument } from "../lib/recent";
import { getJSON } from "../lib/storage";

export default function Instrument() {
  const { id } = useParams();
  const instrumentId = Number(id);
  const { data: inst } = useInstrument(instrumentId);
  const sync = useSyncPrices(instrumentId);

  const [range, setRange] = useState<"90d" | "180d" | "365d" | "max">("180d");
  const [runId, setRunId] = useState<number | undefined>();

  // record recent instruments
  useEffect(() => {
    if (inst?.id && inst?.symbol) {
      pushRecentInstrument({
        id: inst.id,
        symbol: inst.symbol,
        name: inst.name,
      });
    }
  }, [inst?.id, inst?.symbol, inst?.name]);

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

  const { data: candlesRes, isLoading: isCandles } = useCandles(
    instrumentId,
    fromISO
  );
  const candles = (candlesRes?.candles || []).map((c: any) => ({
    ts: c.ts,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
    volume: c.volume,
  }));

  const { data: indRes, isLoading: isInd } = useIndicators(
    instrumentId,
    fromISO
  );
  const { data: sentRes, isLoading: isSent } = useSentiment(instrumentId, 14);
  const { data: fcRes } = useForecast(runId);
  const startFc = useStartForecast();
  const { data: newsRes, isLoading: isNews } = useNews(instrumentId, 7);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            {inst?.symbol ?? `Instrument #${instrumentId}`}
          </h1>
          {inst?.name && <p className="text-sm text-text-muted">{inst.name}</p>}
        </div>
        <div className="flex items-center gap-3">
          <RangePicker value={range} onChange={(v) => setRange(v as any)} />
          <button className="btn-ghost h-10" /* Sync handler */>
            Sync Prices
          </button>
          <button className="btn h-10" /* Forecast handler */>
            Forecast 7d
          </button>
        </div>
      </div>
      <div className="card p-4">
        {(isCandles || isInd) && <Spinner label="Loading chart data…" />}
        {!isCandles && !isInd && (
          <PriceChart
            candles={candles}
            indicators={indRes?.indicators}
            forecast={fcRes ? { points: fcRes.points } : undefined}
            title={`${inst?.symbol ?? "Instrument"} — Price & Indicators`}
          />
        )}
      </div>
      {isSent && <div className="card h-36 animate-pulse" />}
      {!isSent && sentRes?.daily?.length ? (
        <div className="card p-4">
          <h2 className="mb-3 font-medium">News Sentiment (14d)</h2>
          <SentimentChart daily={sentRes.daily} />
        </div>
      ) : null}
      <div className="card p-4">
        <h2 className="mb-3 font-medium">Latest News</h2>
        {isNews ? (
          <Skeleton className="h-24" />
        ) : (
          <NewsList articles={newsRes?.articles || []} />
        )}
      </div>
    </div>
  );
}
