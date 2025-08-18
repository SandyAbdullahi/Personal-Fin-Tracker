// src/features/goals/api.ts
import { apiFetch, getJson, postJson } from "../../lib/api";

export type GoalDTO = {
  id: number;
  name: string;
  target_amount: string;      // DRF returns decimals as strings
  current_amount: string;
  remaining_amount: string;
  target_date: string | null; // "YYYY-MM-DD" or null
};

export type Paginated<T> = { results: T[]; count?: number; next?: string | null; previous?: string | null };

export type GoalPayload = {
  name: string;
  target_amount: string | number;
  current_amount?: string | number;
  target_date?: string | null;
};

// List goals (optionally filter by name with ?name__icontains=)
export async function listGoals(search?: string): Promise<Paginated<GoalDTO>> {
  const qs = search ? `?name__icontains=${encodeURIComponent(search)}` : "";
  return getJson<Paginated<GoalDTO>>(`/api/finance/goals/${qs}`);
}

// Create
export function createGoal(payload: GoalPayload): Promise<GoalDTO> {
  const body = {
    ...payload,
    target_amount: payload.target_amount.toString(),
    ...(payload.current_amount != null ? { current_amount: payload.current_amount.toString() } : {}),
  };
  return postJson<GoalDTO>("/api/finance/goals/", body);
}

// Patch
async function patchJson<T>(path: string, body: unknown): Promise<T> {
  const res = await apiFetch(path, { method: "PATCH", body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`PATCH ${path} failed: ${res.status} ${await res.text().catch(() => "")}`);
  return res.json();
}

export function updateGoal(id: number, patch: Partial<GoalPayload>): Promise<GoalDTO> {
  const body: any = { ...patch };
  if (body.target_amount != null) body.target_amount = String(body.target_amount);
  if (body.current_amount != null) body.current_amount = String(body.current_amount);
  return patchJson<GoalDTO>(`/api/finance/goals/${id}/`, body);
}

// Delete
export async function deleteGoal(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/goals/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE /goals/${id} failed: ${res.status}`);
}
