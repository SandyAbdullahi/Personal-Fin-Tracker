import React, { createContext, useContext, useEffect, useState } from "react";

type AuthContextType = {
  initializing: boolean;
  isAuthenticated: boolean;
  accessToken: string | null;
  user: any | null;
  login: (access: string, refresh: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({
  initializing: true,
  isAuthenticated: false,
  accessToken: null,
  user: null,
  login: async () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

function parseJwt(token: string) {
  try {
    const [, payload] = token.split(".");
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
  } catch {
    return null;
  }
}

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [initializing, setInitializing] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUser] = useState<any | null>(null);

  useEffect(() => {
    const a = localStorage.getItem("access");
    const r = localStorage.getItem("refresh");
    if (a && r) {
      setAccessToken(a);
      setRefreshToken(r);
      setUser(parseJwt(a));
    }
    setInitializing(false);
  }, []);

  const login = async (access: string, refresh: string) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
    setUser(parseJwt(access));
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  };

  return (
    <AuthContext.Provider
      value={{
        initializing,
        isAuthenticated: !!accessToken,
        accessToken,
        user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
