import { Link } from "react-router-dom";
import NewPortfolio from "../components/NewPortfolio";
import { usePortfolios } from "../hooks/usePortfolios";
import { getRecentInstruments } from "../lib/recent";

export default function Dashboard() {
  const { data: portfolios } = usePortfolios();
  const recents = getRecentInstruments();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="text-sm opacity-70">Your Portfolios</div>
          <div className="mt-3"><NewPortfolio /></div>
          <ul className="mt-3 text-sm space-y-1">
            {(portfolios || []).map((p) => (
              <li key={String(p.id)}>
                <Link className="underline" to={`/portfolio/${p.id}`}>
                  {p.name || `Portfolio ${p.id}`}
                </Link>
                {p.base_currency ? <span className="opacity-60"> · {p.base_currency}</span> : null}
              </li>
            ))}
            {!portfolios?.length && <li className="opacity-60">No portfolios</li>}
          </ul>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 md:col-span-2">
          <div className="text-sm opacity-70">Recent Instruments</div>
          <div className="mt-3 grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {recents.length ? recents.map((r) => (
              <Link key={r.id} to={`/instrument/${r.id}`} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:bg-slate-800/60">
                <div className="font-mono">{r.symbol}</div>
                {r.name ? <div className="text-xs opacity-60">{r.name}</div> : null}
              </Link>
            )) : <div className="opacity-60 text-sm">No recent instruments</div>}
          </div>
        </div>
      </div>
   </div>
  );
}
