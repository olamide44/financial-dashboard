import Papa from "papaparse";
import toast from "react-hot-toast";
import { useBulkUpsertHoldings } from "../hooks/useBulkHoldings";

type Props = { portfolioId: string | number };
export default function HoldingsImport({ portfolioId }: Props) {
  const upsert = useBulkUpsertHoldings(portfolioId);

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (res) => {
        try {
          // Expect headers: symbol, qty, cost_basis (case-insensitive)
          const rows = (res.data as any[]).map(r => ({
            symbol: String(r.symbol || r.SYMBOL || r.ticker || "").trim().toUpperCase(),
            qty: Number(r.qty || r.QTY || r.quantity || 0),
            cost_basis: r.cost_basis != null ? Number(r.cost_basis) : undefined,
          })).filter(r => r.symbol && !isNaN(r.qty) && r.qty !== 0);
          if (!rows.length) { toast.error("No valid rows"); return; }
          await upsert.mutateAsync(rows);
          toast.success(`Imported ${rows.length} rows`);
        } catch (err:any) {
          toast.error(String(err?.response?.data?.detail || "Import failed"));
        } finally { e.target.value = ""; }
      },
      error: () => toast.error("CSV parse failed"),
    });
  }

  return (
    <label className="inline-flex items-center gap-2 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 cursor-pointer">
      <input type="file" accept=".csv" className="hidden" onChange={onFile} />
      Import CSV
    </label>
  );
}
