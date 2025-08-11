// src/app/Layout.tsx
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth/AuthContext"; // ← fix path

export default function Layout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    // optional: force redirect after logout
    navigate("/login", { replace: true });
  };

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-2 py-1 rounded ${isActive ? "font-semibold underline" : ""}`;

  return (
    <div className="min-h-screen">
      <nav className="p-4 border-b flex gap-4 items-center">
        <NavLink to="/" end className={linkClass}>
          Summary
        </NavLink>
        <NavLink to="/transactions" className={linkClass}>
          Transactions
        </NavLink>
        <button className="ml-auto" onClick={handleLogout}>
          Log out
        </button>
      </nav>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  );
}
