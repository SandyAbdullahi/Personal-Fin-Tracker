// src/features/budgets/EditBudgetModal.tsx
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch, getJson } from "../../lib/api";
import type { Budget } from "./api";

type Props = {
  open: boolean;
  budget: Budget | null;
  onClose: () => void;
};

type Category = { id: number; name: string };

export default function EditBudgetModal({ open, budget, onClose }: Props) {
  const qc = useQueryClient();

  const [categoryId, setCategoryId] = useState<number | "">("");
  const [period, setPeriod] = useState<"M" | "Y">("M");
  const [limit, setLimit] = useState<string>("");

  // Load categories for the select
  const { data: categories } = useQuery({
    queryKey: ["categories", "all"],
    queryFn: async () => {
      // Pull a page large enough for most users; tweak if you paginate
      const res = await getJson<{ results: Category[] }>(
        "/api/finance/categories/?page_size=1000"
      );
      return res.results;
    },
  });

  // Pre-fill when opening
  useEffect(() => {
    if (open && budget) {
      setCategoryId(budget.category);
      setPeriod(budget.period);
      setLimit(budget.limit);
    }
  }, [open, budget]);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!budget) throw new Error("No budget selected");
      const res = await apiFetch(`/api/finance/budgets/${budget.id}/`, {
        method: "PATCH",
        body: JSON.stringify({
          category: categoryId || budget.category,
          period,
          limit,
        }),
      });
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Update failed: ${res.status} ${txt}`);
      }
      return res.json();
    },
    onSuccess: () => {
      // Refresh list + any detail queries
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["budget", budget?.id] });
      onClose();
    },
  });

  const canSubmit = useMemo(() => {
    return !!limit && (categoryId !== "" || !!budget?.category);
  }, [limit, categoryId, budget]);

  if (!open || !budget) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Edit Budget</h2>

        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) mutation.mutate();
          }}
        >
          <div className="grid gap-1">
            <label className="text-sm font-medium">Category</label>
            <select
              className="border rounded px-3 py-2"
              value={categoryId === "" ? "" : Number(categoryId)}
              onChange={(e) =>
                setCategoryId(e.target.value ? Number(e.target.value) : "")
              }
            >
              <option value="">(keep current)</option>
              {(categories ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            <div className="text-xs text-gray-500">
              Current: #{budget.category}
            </div>
          </div>

          <div className="grid gap-1">
            <label className="text-sm font-medium">Limit</label>
            <input
              type="number"
              min={0}
              step="0.01"
              className="border rounded px-3 py-2"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              required
            />
          </div>

          <div className="grid gap-1">
            <label className="text-sm font-medium">Period</label>
            <select
              className="border rounded px-3 py-2"
              value={period}
              onChange={(e) => setPeriod(e.target.value as "M" | "Y")}
            >
              <option value="M">Monthly</option>
              <option value="Y">Yearly</option>
            </select>
          </div>

          {mutation.isError ? (
            <div className="text-sm text-red-600">
              {(mutation.error as Error).message}
            </div>
          ) : null}

          <div className="flex gap-2 justify-end pt-2">
            <button
              type="button"
              className="px-3 py-2 rounded border"
              onClick={() => onClose()}
              disabled={mutation.isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
              disabled={!canSubmit || mutation.isLoading}
            >
              {mutation.isLoading ? "Saving…" : "Save changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
