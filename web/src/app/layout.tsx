import { Outlet, NavLink } from "react-router-dom";

export function Layout() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 p-4 border-r">
        <nav className="space-y-2">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/transactions">Transactions</NavLink>
          {/* Budgets, Goals, Debts, Transfers, Recurring */}
        </nav>
      </aside>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
