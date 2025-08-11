// src/features/categories/api.ts
import { useQuery } from "@tanstack/react-query";
import { getJson } from "../../lib/api";

export type Category = { id: number; name: string };

export async function fetchCategories(): Promise<{ results: Category[] }> {
  // Your categories endpoint is paginated via DRF, so return {results:[]}
  return getJson<{ results: Category[] }>("/api/finance/categories/");
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });
}
