import { useQuery } from "@tanstack/react-query";
import api from "../../api/client";
import { EP } from "../../api/endpoints";

export function useSummary() {
  return useQuery({
    queryKey: ["summary"],
    queryFn: async () => (await api.get(EP.summary)).data,
  });
}
