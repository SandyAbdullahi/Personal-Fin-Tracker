// src/features/budgets/BudgetsPage.tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listBudgets,
  createBudget,
  updateBudget,
  deleteBudget,
  type Budget,
  type BudgetPayload,
} from "./api";
import { fetchCategories, type CategoryDTO } from "../categories/api";

export default function BudgetsPage() {
  const qc = useQueryClient();

  // Fetch budgets
  const { data: budgets = [], isLoading: budgetsLoading, error: budgetsError } = useQuery({
    queryKey: ["budgets"],
    queryFn: () => listBudgets(),
  });

  // Fetch categories (so we can show names and power the form)
  const { data: categories = [], isLoading: catsLoading, error: catsError } = useQuery({
    queryKey: ["categories"],
    queryFn: () => fetchCategories(),
  });

  const catNameById = useMemo(() => {
    const m = new Map<number, string>();
    (categories as CategoryDTO[]).forEach((c) => m.set(c.id, c.name));
    return m;
  }, [categories]);

  // Form state
  const [form, setForm] = useState<BudgetPayload>({ category: 0, limit: "", period: "M" });
  const [editing, setEditing] = useState<Budget | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Mutations
  const createMut = useMutation({
    mutationFn: (payload: BudgetPayload) => createBudget(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setForm({ category: 0, limit: "", period: "M" });
      setErrorMsg(null);
    },
    onError: async (err: any) => setErrorMsg(err?.message ?? "Create failed"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<BudgetPayload> }) =>
      updateBudget(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setEditing(null);
      setForm({ category: 0, limit: "", period: "M" });
      setErrorMsg(null);
    },
    onError: async (err: any) => setErrorMsg(err?.message ?? "Update failed"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteBudget(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["budgets"] }),
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    if (editing) {
      updateMut.mutate({
        id: editing.id,
        payload: {
          category: form.category,
          limit: form.limit,
          period: form.period,
        },
      });
    } else {
      createMut.mutate(form);
    }
  };

  const onEdit = (b: Budget) => {
    setEditing(b);
    setForm({ category: b.category, limit: String(b.limit), period: b.period });
  };

  const onCancel = () => {
    setEditing(null);
    setForm({ category: 0, limit: "", period: "M" });
    setErrorMsg(null);
  };

  if (budgetsLoading || catsLoading) return <div>Loading…</div>;
  if (budgetsError) return <div className="text-red-600">Failed to load budgets.</div>;
  if (catsError) return <div className="text-red-600">Failed to load categories.</div>;

  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Budgets</h1>

      <form onSubmit={onSubmit} className="mb-6 flex gap-2 items-end">
        <div>
          <label className="block text-sm mb-1">Category</label>
          <select
            className="border rounded px-2 py-1"
            value={form.category}
            onChange={(e) => setForm((f) => ({ ...f, category: Number(e.target.value) }))}
            required
          >
            <option value={0} disabled>
              Select a category…
            </option>
            {(categories as CategoryDTO[]).map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">Limit (KES)</label>
          <input
            className="border rounded px-2 py-1"
            type="number"
            step="0.01"
            value={form.limit}
            onChange={(e) => setForm((f) => ({ ...f, limit: e.target.value }))}
            required
          />
        </div>

        <div>
          <label className="block text-sm mb-1">Period</label>
          <select
            className="border rounded px-2 py-1"
            value={form.period}
            onChange={(e) => setForm((f) => ({ ...f, period: e.target.value as "M" | "Y" }))}
          >
            <option value="M">Monthly</option>
            <option value="Y">Yearly</option>
          </select>
        </div>

        <button
          type="submit"
          className="px-3 py-2 rounded bg-blue-600 text-white"
          disabled={createMut.isPending || updateMut.isPending}
        >
          {editing ? "Update" : "Create"}
        </button>
        {editing && (
          <button type="button" className="px-3 py-2 rounded border" onClick={onCancel}>
            Cancel
          </button>
        )}
        {errorMsg && <div className="text-red-600 ml-2">{errorMsg}</div>}
      </form>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b text-left">
            <th className="py-2 pr-2">Category</th>
            <th className="py-2 pr-2">Limit</th>
            <th className="py-2 pr-2">Spent</th>
            <th className="py-2 pr-2">Remaining</th>
            <th className="py-2 pr-2">Used %</th>
            <th className="py-2 pr-2"></th>
          </tr>
        </thead>
        <tbody>
          {budgets.map((b) => (
            <tr key={b.id} className="border-b">
              <td className="py-2 pr-2">{catNameById.get(b.category) ?? b.category}</td>
              <td className="py-2 pr-2">{b.limit}</td>
              <td className="py-2 pr-2">{b.amount_spent ?? b.spent ?? "0.00"}</td>
              <td className="py-2 pr-2">{b.remaining ?? ""}</td>
              <td className="py-2 pr-2">
                {typeof b.percent_used === "number" ? b.percent_used.toFixed(1) : ""}
              </td>
              <td className="py-2 pr-2 flex gap-2">
                <button className="px-2 py-1 border rounded" onClick={() => onEdit(b)}>
                  Edit
                </button>
                <button
                  className="px-2 py-1 border rounded text-red-600"
                  onClick={() => deleteMut.mutate(b.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
          {budgets.length === 0 && (
            <tr>
              <td colSpan={6} className="py-6 text-center text-gray-500">
                No budgets yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
