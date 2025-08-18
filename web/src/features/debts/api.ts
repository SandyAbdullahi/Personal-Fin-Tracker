// src/features/debts/api.ts
import { getJson, postJson, apiFetch } from "../../lib/api";

// ---------------- Debts ----------------
export type DebtDTO = {
  id: number;
  name: string;
  principal: string;
  interest_rate: string;
  minimum_payment: string;
  opened_date: string | null;
  category: number | null;
  balance: string; // computed property from backend
};

export type DebtPayload = {
  name: string;
  principal: string;
  interest_rate: string;
  minimum_payment: string;
  opened_date?: string | null;
  category?: number | null;
};

export async function listDebts(): Promise<{ results: DebtDTO[] }> {
  return getJson("/api/finance/debts/");
}

export async function createDebt(payload: DebtPayload): Promise<DebtDTO> {
  return postJson("/api/finance/debts/", payload);
}

export async function updateDebt(
  id: number,
  patch: Partial<DebtPayload>
): Promise<DebtDTO> {
  const res = await apiFetch(`/api/finance/debts/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`PATCH debt failed: ${res.status}`);
  return res.json();
}

export async function deleteDebt(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/debts/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE debt failed: ${res.status}`);
}

// ---------------- Payments ----------------
export type PaymentDTO = {
  id: number;
  debt: number;
  amount: string;
  date: string;
  memo?: string;
};

export type PaymentPayload = {
  debt: number;
  amount: string;
  date: string;
  memo?: string;
};

export async function listPayments(
  debtId: number
): Promise<{ results: PaymentDTO[] }> {
  return getJson(`/api/finance/payments/?debt=${debtId}`);
}

export async function createPayment(
  payload: PaymentPayload
): Promise<PaymentDTO> {
  return postJson("/api/finance/payments/", payload);
}

export async function deletePayment(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/payments/${id}/`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE payment failed: ${res.status}`);
}
