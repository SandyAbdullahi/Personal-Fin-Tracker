// src/components/ProtectedRoute.tsx
import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth/AuthContext";

type Props = { children: ReactNode };

export const ProtectedRoute = ({ children }: Props) => {
  const { isAuthenticated, hydrated } = useAuth();
  const location = useLocation();

  if (!hydrated) return null; // or a tiny spinner

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <>{children}</>;
};
