import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useLogin } from "../hooks/useAuth";


export default function Login() {
  const navigate = useNavigate();
  const location = useLocation() as any;
  const from = location.state?.from?.pathname || "/";
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const { mutateAsync, isPending, isError, error } = useLogin();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutateAsync({ email, password });
    navigate(from, { replace: true });
  };

  return (
    <div className="max-w-md mx-auto mt-24 p-6 bg-slate-900/60 rounded-xl border border-slate-800">
      <h1 className="text-xl font-semibold mb-4">Sign in</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <input className="w-full px-3 py-2 bg-slate-800 rounded" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="Email" />
        <input className="w-full px-3 py-2 bg-slate-800 rounded" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Password" />
        <button disabled={isPending} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50">
          {isPending ? "Signing in..." : "Sign in"}
        </button>
        {isError && <p className="text-red-400 text-sm">{String((error as any)?.response?.data?.detail || error)}</p>}
      </form>
      <div className="text-sm mt-3">
        No account? <a href="/signup" className="underline">Create one</a>
      </div>
    </div>
  );
}
