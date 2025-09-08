import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { usePortfolios } from "../hooks/usePortfolios";
import { logout } from "../lib/auth";
import { getJSON, setJSON } from "../lib/storage";
import SearchBox from "./SearchBox";


export default function Nav() {

  const navigate = useNavigate();
  const { data: portfolios, isLoading } = usePortfolios();
  const [selectedId, setSelectedId] = useState<string>("");

  // load saved selection
  useEffect(() => {
    const saved = getJSON<string>("selected_portfolio_id");
    if (saved) setSelectedId(String(saved));
  }, []);

  // default to first portfolio if none saved
  useEffect(() => {
    if (!selectedId && portfolios && portfolios.length) {
      const first = String(portfolios[0].id);
      setSelectedId(first);
      setJSON("selected_portfolio_id", first);
    }
  }, [portfolios, selectedId]);
  return (
    <header className="border-b border-slate-800/60 bg-slate-900/80 backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/" className="font-semibold">AI Finance Dashboard</Link>
          <SearchBox />
        </div>
        <nav className="flex items-center gap-4 text-sm">
          {/* Portfolio selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs opacity-70">Portfolio</span>
            <select
              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-sm min-w-40"
              value={selectedId}
              onChange={(e) => {
                const id = e.target.value;
                setSelectedId(id);
                setJSON("selected_portfolio_id", id);
                navigate(`/portfolio/${id}`);
              }}
              disabled={isLoading || !portfolios?.length}
            >
              {isLoading && <option>Loading…</option>}
              {!isLoading && (!portfolios || portfolios.length === 0) && (
                <option>No portfolios</option>
              )}
              {!isLoading &&
                portfolios?.map((p) => (
                  <option key={String(p.id)} value={String(p.id)}>
                    {p.name || `Portfolio ${p.id}`}
                  </option>
                ))}
            </select>
          </div>
          <Link to="/">Dashboard</Link>
          <button
            onClick={() => { logout(); window.location.href = "/login"; }}
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700"
          >
            Logout
          </button>
        </nav>
      </div>
    </header>
  );
}
