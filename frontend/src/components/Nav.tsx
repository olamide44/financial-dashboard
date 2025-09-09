import { ChevronDown } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { usePortfolios } from "../hooks/usePortfolios";
import { logout } from "../lib/auth";
import { getJSON, setJSON } from "../lib/storage";
import SearchBox from "./SearchBox";
import ThemeToggle from "./ThemeToggle";

export default function Nav() {
  const navigate = useNavigate();
  const { data: portfolios, isLoading } = usePortfolios();
  const [selectedId, setSelectedId] = useState<string>("");

  useEffect(() => {
    const saved = getJSON<string>("selected_portfolio_id");
    if (saved) setSelectedId(String(saved));
  }, []);
  useEffect(() => {
    if (!selectedId && portfolios?.length) {
      const id = String(portfolios[0].id);
      setSelectedId(id);
      setJSON("selected_portfolio_id", id);
    }
  }, [portfolios, selectedId]);

  return (
    <header className="sticky top-0 z-30 border-b border-border/70 backdrop-blur bg-bg/80">
      <div className="container h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="text-lg font-semibold tracking-tight">AI Finance</Link>
          <div className="hidden md:block w-72"><SearchBox /></div>
        </div>
        <div className="flex items-center gap-2">
          {/* Portfolio selector */}
          <div className="relative">
            <select
              className="input h-10 w-48 pr-8 appearance-none"
              value={selectedId}
              onChange={(e) => {
                const id = e.target.value;
                setSelectedId(id);
                setJSON("selected_portfolio_id", id);
                navigate(`/portfolio/${id}`);
              }}
              disabled={isLoading || !portfolios?.length}
            >
              {isLoading && <option>Loading...</option>}
              {!isLoading && portfolios?.map((p) => (
                <option key={String(p.id)} value={String(p.id)}>
                  {p.name || `Portfolio ${p.id}`}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none opacity-60" size={16}/>
          </div>

          <ThemeToggle />
          <button
            onClick={() => { logout(); window.location.href = "/login"; }}
            className="btn-ghost h-10 px-3 rounded-xl"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
