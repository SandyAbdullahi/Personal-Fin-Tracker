import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth/AuthContext";

type Props = { children: ReactNode };

export const ProtectedRoute = ({ children }: Props) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) return null; // or a tiny spinner

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return <>{children}</>;
};

export default ProtectedRoute;
