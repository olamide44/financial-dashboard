import {
    Chart as ChartJS,
    Filler,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    TimeScale,
    Title,
    Tooltip,
} from "chart.js";
import "chartjs-adapter-date-fns";
import { Line } from "react-chartjs-2";

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler, Title);

type Candle = { ts: string; open: number; high: number; low: number; close: number; volume?: number };
type IndicatorPoint = { ts: string; v: number | null };
type Indicators = Record<string, IndicatorPoint[]>;

type Props = {
  candles: Candle[];
  indicators?: Indicators; // keys like 'sma_20','ema_200','rsi_14' (we'll use SMA/EMA here)
  forecast?: { points: { ts: string; yhat: number; yhat_lower: number; yhat_upper: number }[] };
  title?: string;
};

export default function PriceChart({ candles, indicators, forecast, title }: Props) {
  const labels = candles.map((c) => c.ts);
  const priceData = candles.map((c) => c.close);

  const mkLine = (label: string, arr: (number | null)[], dash = false) => ({
    label,
    data: arr,
    borderWidth: 1.5,
    borderDash: dash ? [5, 4] : undefined,
    pointRadius: 0,
    parsing: false,
  });

  const sma20 = indicators?.["sma_20"]?.map((p) => (p.v ?? null)) ?? [];
  const sma50 = indicators?.["sma_50"]?.map((p) => (p.v ?? null)) ?? [];
  const ema200 = indicators?.["ema_200"]?.map((p) => (p.v ?? null)) ?? [];

  // Forecast band (fill between upper & lower)
  const fts = forecast?.points?.map((p) => p.ts) ?? [];
  const fy = forecast?.points?.map((p) => p.yhat) ?? [];
  const fyl = forecast?.points?.map((p) => p.yhat_lower) ?? [];
  const fyu = forecast?.points?.map((p) => p.yhat_upper) ?? [];

  const data = {
    labels,
    datasets: [
      {
        label: "Close",
        data: priceData,
        borderWidth: 1.8,
        pointRadius: 0,
        parsing: false,
      },
      mkLine("SMA 20", sma20),
      mkLine("SMA 50", sma50),
      mkLine("EMA 200", ema200, true),
      // Forecast band (render as separate chart area appended after last real candle)
    ] as any[],
  };

  // append forecast datasets with a gap (Chart.js will show them to the right by labels)
  if (fy.length) {
    data.labels = [...labels, ...fts];

    // padding arrays to align with combined labels
    const pad = (arr: any[]) => [...arr, ...Array(fts.length).fill(null)];
    data.datasets[0].data = pad(priceData);
    data.datasets[1].data = pad(sma20);
    data.datasets[2].data = pad(sma50);
    data.datasets[3].data = pad(ema200);

    const upper = Array(labels.length).fill(null).concat(fyu);
    const lower = Array(labels.length).fill(null).concat(fyl);
    const mid   = Array(labels.length).fill(null).concat(fy);

    data.datasets.push({
      label: "Forecast Upper",
      data: upper,
      pointRadius: 0,
      borderWidth: 0,
      fill: "-1", // will fill down to previous dataset (lower), set order accordingly
      order: 3,
    });
    data.datasets.push({
      label: "Forecast Lower",
      data: lower,
      pointRadius: 0,
      borderWidth: 0,
      order: 2,
    });
    data.datasets.push({
      label: "Forecast Mid",
      data: mid,
      pointRadius: 0,
      borderWidth: 1,
      borderDash: [4, 3],
      order: 4,
    });
  }

  const options: any = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: !!title, text: title },
      tooltip: { mode: "index", intersect: false },
    },
    interaction: { mode: "nearest", intersect: false },
    scales: {
      x: { type: "time", time: { unit: "day" }, grid: { display: false } },
      y: { ticks: { callback: (v: number) => v.toFixed(2) } },
    },
  };

  return <Line options={options} data={data} />;
}
