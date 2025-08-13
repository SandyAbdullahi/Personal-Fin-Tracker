import { getJson, postJson, apiFetch } from "../../lib/api";

export type Budget = {
  id: number;
  category: number;
  limit: string;
  period: "M" | "Y";
  amount_spent?: string;
  remaining?: string;
  percent_used?: number;
};

export async function listBudgets(): Promise<Budget[]> {
  const raw = await getJson<any>("/api/finance/budgets/");
  return Array.isArray(raw) ? raw : raw?.results ?? [];
}

export async function createBudget(body: { category: number; limit: string; period: "M" | "Y" }): Promise<Budget> {
  return postJson<Budget>("/api/finance/budgets/", body);
}

export async function deleteBudget(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/budgets/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
}

export async function updateBudget(
  id: number,
  body: { category: number; limit: string; period: "M" | "Y" }
): Promise<Budget> {
  const res = await apiFetch(`/api/finance/budgets/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `Update failed: ${res.status}`);
  }
  return res.json();
}
