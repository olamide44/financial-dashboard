import { useState } from "react";
import toast from "react-hot-toast";
import { useCreateTransaction } from "../hooks/useCreateTransaction";

export default function TransactionForm({ portfolioId }: { portfolioId: string | number }) {
  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState<"buy"|"sell">("buy");
  const [qty, setQty] = useState<number>(0);
  const [price, setPrice] = useState<number>(0);
  const [ts, setTs] = useState<string>("");

  const mutate = useCreateTransaction(portfolioId);

  return (
    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
      <div className="text-sm font-medium mb-2">New Transaction</div>
      <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
        <input className="px-2 py-1.5 rounded bg-slate-800 border border-slate-700" placeholder="Symbol"
               value={symbol} onChange={(e)=>setSymbol(e.target.value.toUpperCase())} />
        <select className="px-2 py-1.5 rounded bg-slate-800 border border-slate-700" value={side} onChange={e=>setSide(e.target.value as any)}>
          <option value="buy">Buy</option><option value="sell">Sell</option>
        </select>
        <input className="px-2 py-1.5 rounded bg-slate-800 border border-slate-700" type="number" placeholder="Qty"
               value={qty} onChange={(e)=>setQty(Number(e.target.value))} />
        <input className="px-2 py-1.5 rounded bg-slate-800 border border-slate-700" type="number" placeholder="Price"
               value={price} onChange={(e)=>setPrice(Number(e.target.value))} />
        <input className="px-2 py-1.5 rounded bg-slate-800 border border-slate-700" type="datetime-local"
               value={ts} onChange={(e)=>setTs(e.target.value)} />
        <button
          onClick={async ()=>{
            try {
              await mutate.mutateAsync({ symbol, side, qty, price, ts: ts || undefined });
              toast.success("Transaction saved");
              setSymbol(""); setQty(0); setPrice(0); setTs("");
            } catch(e:any){ toast.error(String(e?.response?.data?.detail || "Failed")); }
          }}
          disabled={mutate.isPending || !symbol || !qty || !price}
          className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-60"
        >
          {mutate.isPending ? "Saving…" : "Save"}
        </button>
      </div>
    </div>
  );
}
