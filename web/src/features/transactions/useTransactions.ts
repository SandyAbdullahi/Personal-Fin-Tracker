// src/features/transactions/useTransactions.ts
import { useQuery } from "@tanstack/react-query";
import { getJson } from "../../lib/api";
import { useAuth } from "../../lib/auth/AuthContext";

// Shape of a transaction row (adjust if you have extra fields)
export type Transaction = {
  id: number;
  category_id: number;
  amount: string; // DRF renders decimals as strings
  type: "IN" | "EX";
  description: string;
  date: string; // YYYY-MM-DD
  transfer?: number | null;
};

// Typical DRF paginated response
export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

// Allowed query params
export type TxnParams = {
  page?: number;
  page_size?: number;
  ordering?: string; // e.g. "-date" or "amount"
  search?: string;
  category?: number;
  type?: "IN" | "EX";
  date__gte?: string; // YYYY-MM-DD
  date__lte?: string; // YYYY-MM-DD
};

function buildQueryString(params?: TxnParams): string {
  const p = params ?? {};
  const qp = new URLSearchParams();
  (Object.entries(p) as [keyof TxnParams, any][]).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") {
      qp.set(String(k), String(v));
    }
  });
  const qs = qp.toString();
  return qs ? `?${qs}` : "";
}

export function useTransactions(params?: TxnParams) {
  const { userEmail } = useAuth();
  const qs = buildQueryString(params);

  return useQuery<Paginated<Transaction>>({
    queryKey: ["transactions", userEmail, params ?? {}],
    queryFn: async () =>
      getJson<Paginated<Transaction>>(`/api/finance/transactions/${qs}`),
    enabled: Boolean(userEmail), // don’t run until we know who the user is
    staleTime: 0,
    refetchOnMount: "always",
    retry: (failureCount, error) => {
      // Don’t hammer the server on auth errors
      const msg = String(error ?? "");
      if (msg.includes("401")) return false;
      return failureCount < 2;
    },
    // Always return a predictable shape to callers
    select: (data) =>
      data ?? { count: 0, next: null, previous: null, results: [] },
  });
}
