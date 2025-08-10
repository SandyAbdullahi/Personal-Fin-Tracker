import { Outlet, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { logout } = useAuth();
  return (
    <div className="min-h-screen">
      <nav className="p-4 border-b flex gap-4 items-center">
        <NavLink to="/">Summary</NavLink>
        <NavLink to="/transactions">Transactions</NavLink>
        <button className="ml-auto" onClick={logout}>Log out</button>
      </nav>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  );
}
