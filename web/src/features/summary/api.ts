// src/features/summary/api.ts
import { getJson } from "../../lib/api";

export type SummaryResponse = {
  income_total: string;
  expense_total: string;
  by_category: { name: string; total: string }[];
  goals: any[];
};

export const fetchSummary = () => getJson<SummaryResponse>("/api/finance/summary/");
