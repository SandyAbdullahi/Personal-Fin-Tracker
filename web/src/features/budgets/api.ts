// src/features/budgets/api.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getJson, postJson } from "../../lib/api";

export type Budget = {
  id: number;
  category: number;              // FK id
  limit: string;                 // Decimal as string from API
  period: "M" | "Y";
  amount_spent: string;          // "123.45"
  remaining: string;             // "876.55"
  percent_used: number;          // 0..100
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type BudgetsParams = {
  page?: number;
  category?: number;
  ordering?: "created" | "-created" | "limit" | "-limit" | "remaining" | "-remaining" | "percent_used" | "-percent_used";
};

export async function fetchBudgets(params: BudgetsParams = {}): Promise<Paginated<Budget>> {
  const qs = new URLSearchParams();
  if (params.page) qs.set("page", String(params.page));
  if (params.category) qs.set("category", String(params.category));
  if (params.ordering) qs.set("ordering", params.ordering);
  const url = `/api/finance/budgets/${qs.toString() ? `?${qs.toString()}` : ""}`;
  return getJson<Paginated<Budget>>(url);
}

export function useBudgets(params: BudgetsParams = {}) {
  return useQuery({
    queryKey: ["budgets", params],
    queryFn: () => fetchBudgets(params),
    keepPreviousData: true,
  });
}

export type CreateBudgetInput = {
  category: number;
  limit: number | string;
  period: "M" | "Y";
};

export function createBudget(input: CreateBudgetInput) {
  return postJson<Budget>("/api/finance/budgets/", input);
}

export function useCreateBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createBudget,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["summary"] }); // refresh summary progress too
    },
  });
}
