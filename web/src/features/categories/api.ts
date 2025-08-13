// src/features/categories/api.ts
import { getJson } from "../../lib/api";

export type Category = { id: number; name: string };

// Return a flat array whether the API is paginated or not.
export async function fetchCategories(): Promise<Category[]> {
  const data = await getJson<any>("/api/finance/categories/");
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}
