import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  userEmail: string | null;
};

type AuthContextValue = AuthState & {
  isAuthenticated: boolean;
  loading: boolean;
  login: (tokens: { access: string; refresh: string }, email: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    accessToken: null,
    refreshToken: null,
    userEmail: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const accessToken = localStorage.getItem("accessToken");
    const refreshToken = localStorage.getItem("refreshToken");
    const userEmail = localStorage.getItem("userEmail");
    if (accessToken && refreshToken) {
      setState({ accessToken, refreshToken, userEmail });
    }
    setLoading(false);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      loading,
      isAuthenticated: Boolean(state.accessToken),
      login: (tokens, email) => {
        localStorage.setItem("accessToken", tokens.access);
        localStorage.setItem("refreshToken", tokens.refresh);
        localStorage.setItem("userEmail", email);
        setState({
          accessToken: tokens.access,
          refreshToken: tokens.refresh,
          userEmail: email,
        });
      },
      logout: () => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("userEmail");
        setState({ accessToken: null, refreshToken: null, userEmail: null });
      },
    }),
    [state, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
