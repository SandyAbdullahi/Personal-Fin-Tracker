// src/features/transfers/api.ts
import { apiFetch, getJson, postJson } from "../../lib/api";

export type TransferDTO = {
  id: number;
  source_category: number;        // category id
  destination_category: number;   // category id
  amount: string;                 // backend returns decimals as strings
  date: string;                   // ISO date
  description: string;
  // If your backend includes them:
  transactions?: number[];        // ids of paired txs (optional)
};

export type TransferPayload = {
  source_category: number;
  destination_category: number;
  amount: string | number;
  date: string;                   // "YYYY-MM-DD"
  description?: string;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

function buildQuery(params: Record<string, unknown> = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    qs.set(k, String(v));
  });
  const s = qs.toString();
  return s ? `?${s}` : "";
}

/** List transfers (supports standard DRF pagination params) */
export async function listTransfers(params?: {
  page?: number;
  page_size?: number;
  ordering?: string;  // e.g. "-date" if you expose it
}) : Promise<Paginated<TransferDTO>> {
  return getJson<Paginated<TransferDTO>>(
    `/api/finance/transfers/${buildQuery(params)}`
  );
}

/** Create a new transfer */
export async function createTransfer(payload: TransferPayload): Promise<TransferDTO> {
  return postJson<TransferDTO>("/api/finance/transfers/", payload);
}

/** Patch an existing transfer */
export async function updateTransfer(
  id: number,
  patch: Partial<TransferPayload>
): Promise<TransferDTO> {
  const res = await apiFetch(`/api/finance/transfers/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`PATCH /transfers/${id} failed: ${res.status} ${txt}`);
  }
  return res.json();
}

/** Delete a transfer */
export async function deleteTransfer(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/transfers/${id}/`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`DELETE /transfers/${id} failed: ${res.status} ${txt}`);
  }
}
