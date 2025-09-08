import { Link } from "react-router-dom";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="text-sm opacity-70">Quick Links</div>
          <ul className="mt-3 list-disc list-inside text-sm space-y-1">
            <li><Link to="/portfolio/1" className="underline">Portfolio #1</Link> (change to your ID)</li>
            <li><Link to="/instrument/1" className="underline">Instrument #1</Link> (change to your ID)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
