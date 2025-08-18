// src/app/Layout.tsx
import { Outlet, NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth/AuthContext";

export default function Layout() {
  const { logout } = useAuth();
  return (
    <div className="min-h-screen">
      <nav className="p-4 border-b flex gap-4 items-center">
        <NavLink to="/">Summary</NavLink>
        <NavLink to="/transactions">Transactions</NavLink>
        <NavLink to="/budgets">Budgets</NavLink>
        <NavLink to="/categories">Categories</NavLink>
        <NavLink to="/transfers">Transfers</NavLink> {/* ← NEW */}
        <button className="ml-auto" onClick={logout}>Log out</button>
      </nav>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  );
}
