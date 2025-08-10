import { createContext, useContext, useMemo, useState } from "react";
import { login as apiLogin } from "../api/auth";
import { tokenStorage } from "../lib/storage";

type AuthCtx = {
  access: string | null;
  refresh: string | null;
  login: (u: string, p: string) => Promise<void>;
  logout: () => void;
  isAuthed: boolean;
};

const Ctx = createContext<AuthCtx | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [access, setAccess] = useState<string | null>(tokenStorage.getAccess());
  const [refresh, setRefresh] = useState<string | null>(tokenStorage.getRefresh());

  const value = useMemo<AuthCtx>(() => ({
      access,
      refresh,
      isAuthed: !!access,
      async login(username, password) {
        const toks = await apiLogin(username, password);
        tokenStorage.setAccess(toks.access);
        tokenStorage.setRefresh(toks.refresh);
        setAccess(toks.access);
        setRefresh(toks.refresh);
      },
      logout() {
        tokenStorage.clear();
        setAccess(null);
        setRefresh(null);
      },
    }),
    [access, refresh]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
