import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { getMe } from "../hooks/useAuth";
import { getAccessToken } from "../lib/auth";

export default function RequireAuth({ children }: { children: ReactNode }) {
  const token = getAccessToken();
  const location = useLocation();
  const [ok, setOk] = useState<boolean | null>(token ? null : false);
  useEffect(() => {
    if (!token) return;
    getMe().then(() => setOk(true)).catch(() => setOk(false));
  }, [token]);
  if (!token || ok === false) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (ok === null) return null; // could show a spinner if you like
  return children;
}
