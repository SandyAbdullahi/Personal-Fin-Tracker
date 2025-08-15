// src/features/categories/hooks.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createCategory,
  deleteCategory,
  listCategories,
  updateCategory,
} from "./api";

import type { CategoryDTO } from "api.ts";
// import { fetchCategories } from "api";
export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: listCategories,
    staleTime: 60_000,
  });
}

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => createCategory(name),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categories"] }),
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => updateCategory(id, name),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categories"] }),
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteCategory(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categories"] }),
  });
}
