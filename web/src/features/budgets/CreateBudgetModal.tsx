// src/features/budgets/CreateBudgetModal.tsx
import { useState } from "react";
import { useCategories } from "../categories/api";
import { useCreateBudget } from "./api";

type Props = {
  open: boolean;
  onClose: () => void;
};

export default function CreateBudgetModal({ open, onClose }: Props) {
  const { data: cats, isLoading: catsLoading } = useCategories();
  const create = useCreateBudget();

  const [category, setCategory] = useState<number | "">("");
  const [limit, setLimit] = useState<string>("");
  const [period, setPeriod] = useState<"M" | "Y">("M");
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!category || !limit) {
      setError("Please choose a category and limit.");
      return;
    }

    try {
      await create.mutateAsync({ category: Number(category), limit, period });
      onClose();
      setCategory("");
      setLimit("");
      setPeriod("M");
    } catch (err: any) {
      setError(err?.message ?? "Failed to create budget");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow p-4 w-full max-w-md">
        <h2 className="text-lg font-semibold mb-3">Create Budget</h2>

        <form onSubmit={submit} className="space-y-3">
          <div>
            <label className="block text-sm mb-1">Category</label>
            <select
              className="w-full border rounded px-2 py-1"
              value={category}
              onChange={(e) => setCategory(e.target.value ? Number(e.target.value) : "")}
              disabled={catsLoading}
            >
              <option value="">Select category…</option>
              {cats?.results?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm mb-1">Limit</label>
            <input
              type="number"
              step="0.01"
              min="0"
              className="w-full border rounded px-2 py-1"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Period</label>
            <select
              className="w-full border rounded px-2 py-1"
              value={period}
              onChange={(e) => setPeriod(e.target.value as "M" | "Y")}
            >
              <option value="M">Monthly</option>
              <option value="Y">Yearly</option>
            </select>
          </div>

          {error && <div className="text-red-600 text-sm">{error}</div>}

          <div className="flex gap-2 justify-end pt-2">
            <button type="button" className="px-3 py-1 border rounded" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-1 rounded bg-blue-600 text-white disabled:opacity-50"
              disabled={create.isPending}
            >
              {create.isPending ? "Saving…" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
