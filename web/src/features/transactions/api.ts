// src/features/transactions/api.ts
import { apiFetch } from "../../lib/api";

// ── Types ────────────────────────────────────────────────────────────────────
export type TransactionDTO = {
  id: number;
  category_id: number;
  amount: string | number;
  type: "IN" | "EX";
  description: string | null;
  date: string; // YYYY-MM-DD
  // transfer?: number | null; // uncomment if your backend returns it
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type TransactionCreate = {
  category_id: number; // required by backend
  amount: string | number;
  type: "IN" | "EX";
  date: string;
  description?: string;
};

export type TransactionQuery = {
  search?: string;
  ordering?: string;
  page?: number;
  category?: number;
  type?: "IN" | "EX";
  min_amount?: number;
  max_amount?: number;
  date__gte?: string;
  date__lte?: string;
};

// ── Helpers ─────────────────────────────────────────────────────────────────
function toQuery(params: Record<string, unknown>): string {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    usp.set(k, String(v));
  });
  const s = usp.toString();
  return s ? `?${s}` : "";
}

// ── API calls ───────────────────────────────────────────────────────────────
export async function listTransactions(
  params: TransactionQuery = {}
): Promise<Paginated<TransactionDTO>> {
  const q = toQuery({
    search: params.search,
    ordering: params.ordering,
    page: params.page,
    category: params.category,
    type: params.type,
    amount__gte: params.min_amount,
    amount__lte: params.max_amount,
    date__gte: params.date__gte,
    date__lte: params.date__lte,
  });
  const res = await apiFetch(`/api/finance/transactions/${q}`);
  if (!res.ok) throw new Error(`Failed to load transactions: ${res.status}`);
  return res.json();
}

export async function getTransaction(id: number): Promise<TransactionDTO> {
  const res = await apiFetch(`/api/finance/transactions/${id}/`);
  if (!res.ok) throw new Error(`Failed to load transaction ${id}: ${res.status}`);
  return res.json();
}

export async function createTransaction(
  body: TransactionCreate
): Promise<TransactionDTO> {
  const res = await apiFetch(`/api/finance/transactions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Create failed: ${res.status} ${txt}`);
  }
  return res.json();
}

export async function updateTransaction(
  id: number,
  patch: Partial<TransactionCreate>
): Promise<TransactionDTO> {
  const res = await apiFetch(`/api/finance/transactions/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Update failed: ${res.status} ${txt}`);
  }
  return res.json();
}

export async function deleteTransaction(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/transactions/${id}/`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
}
