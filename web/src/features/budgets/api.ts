// src/features/budgets/api.ts
import { apiFetch, getJson, postJson } from "../../lib/api";

export type Budget = {
  id: number;
  category: number;
  limit: string;         // Django returns Decimal as string
  period: "M" | "Y";
  amount_spent: string;  // "123.45"
  remaining: string;     // "876.55"
  percent_used: number;  // e.g. 12.3
};

export type BudgetList = {
  results: Budget[];
  count: number;
  next: string | null;
  previous: string | null;
};

export type CreateBudgetPayload = {
  category: number;
  limit: string | number;
  period: "M" | "Y";
};

export type UpdateBudgetPayload = Partial<CreateBudgetPayload>;

export async function listBudgets(params?: Record<string, string | number>) {
  const qs = params
    ? "?" +
      new URLSearchParams(
        Object.entries(params).map(([k, v]) => [k, String(v)])
      ).toString()
    : "";
  return getJson<BudgetList>(`/api/finance/budgets/${qs}`);
}

export async function createBudget(payload: CreateBudgetPayload) {
  return postJson<Budget>("/api/finance/budgets/", payload);
}

export async function updateBudget(id: number, payload: UpdateBudgetPayload) {
  const res = await apiFetch(`/api/finance/budgets/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`PATCH /budgets/${id} failed: ${res.status} ${txt}`);
  }
  return res.json() as Promise<Budget>;
}

export async function deleteBudget(id: number) {
  const res = await apiFetch(`/api/finance/budgets/${id}/`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`DELETE /budgets/${id} failed: ${res.status} ${txt}`);
  }
  return true;
}
