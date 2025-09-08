import { Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, TimeScale, Tooltip } from "chart.js";
import "chartjs-adapter-date-fns";
import { Line } from "react-chartjs-2";
ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

type SeriesPoint = { ts: string; value: number };
export default function PerformanceChart({ series, benchmark }:{
  series: SeriesPoint[]; benchmark?: { ts: string; value: number }[];
}) {
  const labels = series.map((p) => p.ts);
  const normalization = (arr: SeriesPoint[]) => {
    if (!arr.length) return [];
    const base = arr[0].value || 1;
    return arr.map((p) => (p.value / base - 1) * 100);
  };
  const data = {
    labels,
    datasets: [
      { label: "Portfolio %", data: normalization(series), pointRadius: 0, borderWidth: 1.5 },
      ...(benchmark ? [{ label: "Benchmark %", data: normalization(benchmark as any), pointRadius: 0, borderWidth: 1.5 }] : []),
    ],
  };
return (
  <Line
    data={data}
    options={{
      scales: {
        x: { type: "time" },
        y: {
          ticks: {
            callback: (tickValue: string | number) =>
              typeof tickValue === "number" ? `${tickValue}%` : `${tickValue}`,
          },
        },
      },
    }}
  />
);}
