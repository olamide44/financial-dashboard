import {
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    LineElement, PointElement, Tooltip,
} from "chart.js";
import { Chart } from "react-chartjs-2";
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend);

type DaySent = { day: string; total: number; pos: number; neg: number; neu: number; net_score: number };
export default function SentimentChart({ daily }: { daily: DaySent[] }) {
  const labels = daily.map((d) => d.day);
  const data = {
    labels,
    datasets: [
      { type: "bar" as const, label: "Positive", data: daily.map((d) => d.pos) },
      { type: "bar" as const, label: "Negative", data: daily.map((d) => d.neg) },
      { type: "bar" as const, label: "Neutral",  data: daily.map((d) => d.neu) },
      { type: "line" as const, label: "Net Score", data: daily.map((d) => d.net_score), yAxisID: "y1", pointRadius: 0 },
    ],
  };
  return <Chart type="bar" data={data} options={{
    responsive: true,
    scales: { y: { beginAtZero: true }, y1: { position: "right", min: -1, max: 1 } },
  }} />;
}
