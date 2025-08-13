// src/features/transactions/api.ts
import { getJson, postJson, apiFetch } from "../../lib/api";
import { useQuery } from "@tanstack/react-query";

export type Transaction = {
  id: number;
  category_id: number;
  amount: string;
  type: "IN" | "EX";
  description?: string;
  date: string; // YYYY-MM-DD
};

export type TransactionList = {
  count: number;
  results: Transaction[];
};

export type TransactionPayload = {
  category_id: number;
  amount: string | number;
  type: "IN" | "EX";
  date: string; // YYYY-MM-DD
  description?: string;
};

export async function listTransactions(params?: Record<string, string>): Promise<TransactionList> {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  const data = await getJson<any>(`/api/finance/transactions/${qs}`);
  // normalize paginated/non-paginated
  if (Array.isArray(data)) {
    return { count: data.length, results: data };
  }
  return data;
}

export async function createTransaction(payload: TransactionPayload): Promise<Transaction> {
  return postJson<Transaction>("/api/finance/transactions/", payload);
}

// Optional: delete/update helpers if you need them later
export async function deleteTransaction(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/transactions/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE failed: ${res.status}`);
}

export function useTransactions(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["transactions", params],
    queryFn: () => listTransactions(params),
  });
}
