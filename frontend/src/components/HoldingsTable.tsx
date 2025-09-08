import { Link } from "react-router-dom";

type Props = {
  rows: Array<{
    instrument_id: number;
    symbol: string;
    qty: number;
    cost_basis?: number;
    market_value?: number;
    weight?: number;
  }>;
};
export default function HoldingsTable({ rows }: Props) {
  if (!rows?.length) return <div className="text-sm opacity-70">No holdings yet.</div>;
  return (
    <div className="overflow-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left opacity-70">
          <tr>
            <th className="py-2 pr-4">Symbol</th>
            <th className="py-2 pr-4 text-right">Qty</th>
            <th className="py-2 pr-4 text-right">Cost</th>
            <th className="py-2 pr-4 text-right">Value</th>
            <th className="py-2 pr-4 text-right">Weight</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((h) => (
            <tr key={h.instrument_id} className="border-t border-slate-800/70">
              <td className="py-2 pr-4">
                <Link to={`/instrument/${h.instrument_id}`} className="underline font-mono">
                  {h.symbol}
                </Link>
              </td>
              <td className="py-2 pr-4 text-right">{h.qty}</td>
              <td className="py-2 pr-4 text-right">{h.cost_basis ?? "-"}</td>
              <td className="py-2 pr-4 text-right">{h.market_value ?? "-"}</td>
              <td className="py-2 pr-4 text-right">
                {typeof h.weight === "number" ? `${(h.weight * 100).toFixed(1)}%` : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
