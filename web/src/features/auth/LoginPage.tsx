// src/pages/LoginPage.tsx
import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { login } from "../../api/auth"

type FormData = {
  identifier: string;
  password: string;
};

const USERNAME_FIELD =
  (import.meta as any).env?.VITE_JWT_USERNAME_FIELD || "username";
const USER_LABEL = USERNAME_FIELD === "email" ? "Email" : "Username";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState<FormData>({ identifier: "", password: "" });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fromRedirect =
    (location.state as any)?.from?.pathname || "/dashboard";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await login(form.identifier, form.password);
      // Expecting { access, refresh }
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      navigate(fromRedirect, { replace: true });
    } catch (err: any) {
      // Try to surface a helpful error from DRF/SimpleJWT
      const resp = err?.response?.data;
      const detail =
        resp?.detail ||
        resp?.non_field_errors?.[0] ||
        resp?.error ||
        "Invalid credentials. Please try again.";
      setErrorMsg(String(detail));
    } finally {
      setLoading(false);
    }
  }

  function onChange(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "24px",
      }}
    >
      <form
        onSubmit={onSubmit}
        style={{
          width: "100%",
          maxWidth: 420,
          border: "1px solid #e5e7eb",
          borderRadius: 12,
          padding: 24,
          boxShadow: "0 4px 20px rgba(0,0,0,0.04)",
          background: "#fff",
        }}
      >
        <h1 style={{ fontSize: 24, margin: 0, marginBottom: 16 }}>Sign in</h1>
        <p style={{ color: "#6b7280", marginTop: 0, marginBottom: 20 }}>
          Use your {USER_LABEL.toLowerCase()} and password to continue.
        </p>

        <label style={{ display: "block", fontSize: 14, marginBottom: 6 }}>
          {USER_LABEL}
        </label>
        <input
          name="identifier"
          type={USERNAME_FIELD === "email" ? "email" : "text"}
          placeholder={USER_LABEL}
          autoComplete={USERNAME_FIELD}
          value={form.identifier}
          onChange={onChange}
          required
          style={{
            width: "100%",
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #d1d5db",
            marginBottom: 14,
          }}
        />

        <label style={{ display: "block", fontSize: 14, marginBottom: 6 }}>
          Password
        </label>
        <div style={{ position: "relative", marginBottom: 6 }}>
          <input
            name="password"
            type={showPw ? "text" : "password"}
            placeholder="Your password"
            autoComplete="current-password"
            value={form.password}
            onChange={onChange}
            required
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 8,
              border: "1px solid #d1d5db",
            }}
          />
          <button
            type="button"
            onClick={() => setShowPw((s) => !s)}
            style={{
              position: "absolute",
              right: 8,
              top: 8,
              border: "none",
              background: "transparent",
              cursor: "pointer",
              color: "#6b7280",
              padding: 6,
            }}
            aria-label={showPw ? "Hide password" : "Show password"}
          >
            {showPw ? "Hide" : "Show"}
          </button>
        </div>

        {errorMsg && (
          <div
            role="alert"
            style={{
              background: "#fef2f2",
              color: "#991b1b",
              border: "1px solid #fecaca",
              padding: "10px 12px",
              borderRadius: 8,
              marginTop: 8,
              marginBottom: 8,
              fontSize: 14,
            }}
          >
            {errorMsg}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid transparent",
            background: loading ? "#9ca3af" : "#111827",
            color: "#fff",
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: 12,
          }}
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>

        <p style={{ fontSize: 12, color: "#6b7280", marginTop: 12 }}>
          Tip: this form sends{" "}
          <code>{USERNAME_FIELD}</code> to <code>/api/token/</code>.
          Set <code>VITE_JWT_USERNAME_FIELD</code> to <code>email</code> or{" "}
          <code>username</code> in your <code>.env</code>.
        </p>
      </form>
    </div>
  );
}
