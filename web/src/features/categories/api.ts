import { apiFetch, getJson, postJson } from "../../lib/api";

export type CategoryDTO = {
  id: number;
  name: string;
  created?: string;
  updated?: string;
};

// GET /list
export async function fetchCategories(): Promise<CategoryDTO[]> {
  const data = await getJson<any>("/api/finance/categories/");
  return Array.isArray(data) ? data : data.results ?? [];
}

// POST /create
export async function createCategory(payload: { name: string }): Promise<CategoryDTO> {
  return postJson<CategoryDTO>("/api/finance/categories/", payload);
}

// PATCH /update
export async function updateCategory(
  id: number,
  payload: { name: string }
): Promise<CategoryDTO> {
  const res = await apiFetch(`/api/finance/categories/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`PATCH /categories/${id} failed: ${res.status} ${txt}`);
  }
  return res.json();
}

// DELETE /destroy
export async function deleteCategory(id: number): Promise<void> {
  const res = await apiFetch(`/api/finance/categories/${id}/`, { method: "DELETE" });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`DELETE /categories/${id} failed: ${res.status} ${txt}`);
  }
}

// 👇 compatibility so old imports keep working
export { fetchCategories as listCategories };
export type { CategoryDTO as Category };
