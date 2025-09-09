import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useSignup } from "../hooks/useSignup";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const nav = useNavigate();
  const loc = useLocation() as any;
  const from = loc.state?.from?.pathname || "/";
  const { mutateAsync, isPending, isError, error } = useSignup();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutateAsync({ username, password });
    nav(from, { replace: true });
  };

  return (
    <div className="max-w-md mx-auto mt-24 p-6 bg-slate-900/60 rounded-xl border border-slate-800">
      <h1 className="text-xl font-semibold mb-4">Create account</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <input className="w-full px-3 py-2 bg-slate-800 rounded" value={username} onChange={(e)=>setUsername(e.target.value)} placeholder="Email" />
        <input className="w-full px-3 py-2 bg-slate-800 rounded" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Password" />
        <button disabled={isPending} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50">Sign up</button>
        {isError && <p className="text-red-400 text-sm">{String((error as any)?.response?.data?.detail || error)}</p>}
      </form>
      <div className="text-sm mt-3">
        Already have an account? <Link to="/login" className="underline">Log in</Link>
      </div>
    </div>
  );
}
