import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import useDebounce from "../hooks/useDebounce";
import { useSearchInstruments } from "../hooks/useInstruments";

export default function SearchBox() {
  const [q, setQ] = useState("");
  const debounced = useDebounce(q, 250);
  const { data, isFetching } = useSearchInstruments(debounced);

  // close results on ESC
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setQ("");
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const results = Array.isArray(data) ? data.slice(0, 8) : [];

  return (
    <div className="relative w-72">
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search symbols (AAPL, MSFT)…"
        className="w-full px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-700 text-sm outline-none focus:ring-2 focus:ring-blue-600"
      />
      {q && (
        <div className="absolute z-20 mt-1 w-full rounded-lg bg-slate-900 border border-slate-800 shadow-lg">
          {isFetching && (
            <div className="p-2 text-xs text-slate-400">Searching…</div>
          )}
          {!isFetching && results.length === 0 && (
            <div className="p-2 text-xs text-slate-400">No matches</div>
          )}
          {!isFetching &&
            results.map((it: any) => (
              <Link
                key={it.id}
                to={`/instrument/${it.id}`}
                className="block px-3 py-2 text-sm hover:bg-slate-800"
                onClick={() => setQ("")}
              >
                <span className="font-mono">{it.symbol}</span>
                {it.name ? <span className="opacity-70"> — {it.name}</span> : null}
              </Link>
            ))}
        </div>
      )}
    </div>
  );
}
