import { useState } from "react";
import toast from "react-hot-toast";
import { useCreatePortfolio } from "../hooks/useCreatePortfolio";

export default function NewPortfolio() {
  const [name, setName] = useState("");
  const [ccy, setCcy] = useState("USD");
  const create = useCreatePortfolio();

  return (
    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
      <div className="text-sm font-medium mb-2">New Portfolio</div>
      <div className="flex gap-2">
        <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Name"
               className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 flex-1" />
        <input value={ccy} onChange={(e)=>setCcy(e.target.value.toUpperCase())} placeholder="USD"
               className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 w-24" />
        <button
          onClick={async ()=>{
            try { await create.mutateAsync({ name, base_currency: ccy }); toast.success("Portfolio created");
            setName(""); } catch(e:any){ toast.error(String(e?.response?.data?.detail||"Create failed")); }
          }}
          className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60"
          disabled={create.isPending || !name.trim()}
        >
          {create.isPending ? "Creating…" : "Create"}
        </button>
      </div>
    </div>
  );
}
