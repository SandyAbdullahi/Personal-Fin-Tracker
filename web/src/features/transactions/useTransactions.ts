// src/features/transactions/useTransactions.ts
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../../lib/auth/AuthContext";
import { getJson } from "../../lib/api";
import type { Paginated, Transaction } from "./api";

type Params = Record<string, string | number | boolean | undefined | null>;

export function useTransactions(params?: Params) {
  const { isAuthenticated } = useAuth();

  // Always coerce to a plain object
  const safeParams: Record<string, string> = Object.fromEntries(
    Object.entries((params && typeof params === "object" ? params : {}) as Params)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => [k, String(v)])
  );

  const qs = new URLSearchParams(safeParams).toString();
  const url = `/api/finance/transactions/${qs ? `?${qs}` : ""}`;

  return useQuery<Paginated<Transaction>>({
    queryKey: ["transactions", safeParams],
    enabled: isAuthenticated,            // don’t fetch if not logged in
    queryFn: () => getJson(url),
    keepPreviousData: true,
    staleTime: 30_000,
  });
}
