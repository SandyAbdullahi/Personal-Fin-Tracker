// src/features/auth/LoginPage.tsx
import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../lib/auth/AuthContext";
import { apiFetch } from "../../lib/api";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // where to go after login (default "/")
  const from = (location.state as any)?.from?.pathname || "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If we’re already logged in (or just became logged in), bounce out.
  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
         const resp = await apiFetch("/api/token/", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        });

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data?.detail || "Invalid credentials");
      }

      const tokens = (await resp.json()) as { access: string; refresh: string };
      login(tokens, email);

      // navigate explicitly (the <Navigate /> above is a safety net)
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16 p-6 border rounded">
      <h1 className="text-xl mb-4">Sign in</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm mb-1">Email</label>
          <input
            type="email"
            className="w-full border rounded px-3 py-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Password</label>
          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          className="w-full px-3 py-2 rounded bg-black text-white disabled:opacity-50"
          disabled={submitting}
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}
