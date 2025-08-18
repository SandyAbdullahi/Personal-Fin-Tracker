// src/features/budgets/api.ts
import { getJson, postJson, apiFetch } from "../../lib/api";

export type BudgetDTO = {
  id: number;
  category: number;           // FK id
  limit: string;              // DRF Decimal → string
  period: "M" | "Y";

  // annotated / computed (read-only)
  amount_spent: string;       // mapped from spent
  net_transfer: string;       // inbound − outbound
  effective_limit: string;    // limit + net_transfer
  remaining: string;          // effective_limit − amount_spent
  percent_used: number;       // 0..100
};

export type BudgetUpsert = {
  category: number;           // POST/PUT/PATCH expects the FK id
  limit: string | number;
  period: "M" | "Y";
};

type Paginated<T> = {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
};

/** Normalize DRF list (paginated or not) into an array */
function normalizeList<T>(payload: Paginated<T> | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload?.results ?? [];
}

export async function listBudgets(): Promise<BudgetDTO[]> {
  const data = await getJson<Paginated<BudgetDTO> | BudgetDTO[]>("/api/finance/budgets/");
  return normalizeList(data);
}

export async function createBudget(body: BudgetUpsert): Promise<BudgetDTO> {
  return postJson<BudgetDTO>("/api/finance/budgets/", body);
}

export async function updateBudget(id: number, body: Partial<BudgetUpsert>): Promise<BudgetDTO> {
  const res = await apiFetch(`/api/finance/budgets/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`PATCH /budgets/${id} failed: ${res.status} ${txt}`);
  }
  return res.json();
}

export async function deleteBudget(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/budgets/${id}/`, { method: "DELETE" });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`DELETE /budgets/${id} failed: ${res.status} ${txt}`);
  }
}
