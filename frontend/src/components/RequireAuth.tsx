import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { getAccessToken } from "../lib/auth";

export default function RequireAuth({ children }: { children: ReactNode }) {
  const token = getAccessToken();
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}
