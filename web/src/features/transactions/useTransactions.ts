import { useQuery } from "@tanstack/react-query";
import api from "../../api/client";
import { EP } from "../../api/endpoints";

export function useTransactions(params: Record<string, string | number> = {}) {
  return useQuery({
    queryKey: ["transactions", params],
    queryFn: async () => (await api.get(EP.transactions, { params })).data,
  });
}
