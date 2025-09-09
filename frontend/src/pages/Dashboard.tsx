import { Link } from "react-router-dom";
import { usePortfolios } from "../hooks/usePortfolios";
import { getRecentInstruments } from "../lib/recent";

export default function Dashboard() {
  const { data: portfolios } = usePortfolios();
  const recents = getRecentInstruments();

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Overview</h1>
          <p className="text-sm text-text-muted">Welcome back — here’s your snapshot.</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-sm text-text-muted">Portfolios</div>
          <div className="mt-2 space-y-2">
            {(portfolios || []).map((p) => (
              <Link key={String(p.id)} to={`/portfolio/${p.id}`} className="block p-3 rounded-xl bg-bg-soft border border-border hover:border-border-strong transition">
                <div className="font-medium">{p.name || `Portfolio ${p.id}`}</div>
                {p.base_currency && <div className="text-xs text-text-muted mt-0.5">{p.base_currency}</div>}
              </Link>
            ))}
            {!portfolios?.length && <div className="text-sm text-text-muted">No portfolios yet.</div>}
          </div>
        </div>

        <div className="card p-4 md:col-span-2">
          <div className="text-sm text-text-muted">Recent Instruments</div>
          <div className="mt-3 grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {recents.length ? recents.map((r) => (
              <Link key={r.id} to={`/instrument/${r.id}`} className="p-3 rounded-xl bg-bg-soft border border-border hover:border-border-strong transition">
                <div className="font-mono font-medium">{r.symbol}</div>
                {r.name ? <div className="text-xs text-text-muted">{r.name}</div> : null}
              </Link>
            )) : <div className="text-sm text-text-muted">No recent instruments.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
