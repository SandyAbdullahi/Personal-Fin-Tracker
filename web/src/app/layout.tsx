import { Outlet, NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export function Layout() {
  const { isAuthed, logout } = useAuth();
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 p-4 border-r">
        <nav className="space-y-2">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/transactions">Transactions</NavLink>
        </nav>
        {isAuthed && (
          <button className="mt-6 text-sm underline" onClick={logout}>Log out</button>
        )}
      </aside>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
