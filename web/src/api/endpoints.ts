export const API_BASE = import.meta.env.VITE_API_BASE as string;
export const API_PREFIX = import.meta.env.VITE_API_PREFIX as string;

export const EP = {
  summary: `${API_PREFIX}/summary/`,
  transactions: `${API_PREFIX}/transactions/`,
  categories: `${API_PREFIX}/categories/`,
  budgets: `${API_PREFIX}/budgets/`,
  goals: `${API_PREFIX}/goals/`,
  recurrings: `${API_PREFIX}/recurrings/`,
  debts: `${API_PREFIX}/debts/`,
  payments: `${API_PREFIX}/payments/`,
  transfers: `${API_PREFIX}/transfers/`,
} as const;
