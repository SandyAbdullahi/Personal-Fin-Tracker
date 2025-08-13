import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listBudgets,
  createBudget,
  deleteBudget,
  updateBudget, // 👈 make sure this exists in ./api
  type Budget,
} from "./api";
import { fetchCategories as listCategories } from "../categories/api";

export default function BudgetsPage() {
  const qc = useQueryClient();

  // Budgets

  const { data: budgetsRaw, isLoading: budgetsLoading, error: budgetsError } = useQuery({
    queryKey: ["budgets"],
    queryFn: listBudgets, // can return array or paginated object
  });

  const budgets = Array.isArray(budgetsRaw) ? budgetsRaw : budgetsRaw?.results ?? [];

  // Categories (for lookup + selects)
  const {
    data: categories = [],
    isLoading: catsLoading,
    error: catsError,
  } = useQuery<Category[]>({ queryKey: ["categories"], queryFn: listCategories });

  // Map id -> name
  const catMap = useMemo(
    () => new Map<number, string>(categories.map((c) => [c.id, c.name])),
    [categories]
  );
  const catName = (id?: number | string) => {
    if (id == null) return "";
    const num = typeof id === "string" ? parseInt(id, 10) : id;
    return catMap.get(num) ?? `#${id}`;
  };

  // Create form state
  const [form, setForm] = useState<{ category?: number; limit: string; period: "M" | "Y" }>({
    category: undefined,
    limit: "",
    period: "M",
  });

  const createMut = useMutation({
    mutationFn: () =>
      createBudget({
        category: form.category!,
        limit: form.limit,
        period: form.period,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setForm({ category: undefined, limit: "", period: "M" });
    },
  });

  const delMut = useMutation({
    mutationFn: (id: number) => deleteBudget(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["budgets"] }),
  });

  // ---------------- Edit support ----------------
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<{ category?: number; limit: string; period: "M" | "Y" }>({
    category: undefined,
    limit: "",
    period: "M",
  });
  const [editError, setEditError] = useState<string | null>(null);

  const beginEdit = (b: Budget) => {
    setEditingId(b.id);
    setEditError(null);
    setEditForm({
      category: typeof b.category === "string" ? parseInt(b.category, 10) : (b.category as number),
      limit: String(b.limit),
      period: b.period,
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditError(null);
  };

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { category: number; limit: string; period: "M" | "Y" } }) =>
      updateBudget(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setEditingId(null);
      setEditError(null);
    },
    onError: async (err: any) => {
      // Try to surface the server message (e.g. uniqueness error)
      const msg =
        err?.message ??
        (typeof err === "string" ? err : "Update failed");
      setEditError(msg);
    },
  });

  const saveEdit = (id: number) => {
    if (!editForm.category) return;
    updateMut.mutate({ id, payload: { category: editForm.category, limit: editForm.limit, period: editForm.period } });
  };

  // ----------------------------------------------

  if (budgetsLoading || catsLoading) return <div>Loading…</div>;
  if (budgetsError) return <div>Failed to load budgets.</div>;
  if (catsError) return <div>Failed to load categories.</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold">Budgets</h1>

      {/* Create budget */}
      <form
        className="flex flex-wrap gap-2 items-end"
        onSubmit={(e) => {
          e.preventDefault();
          if (!form.category) return;
          createMut.mutate();
        }}
      >
        <div>
          <label className="block text-sm mb-1">Category</label>
          <select
            className="border rounded px-2 py-1"
            value={form.category ?? ""}
            onChange={(e) =>
              setForm((f) => ({ ...f, category: e.target.value ? Number(e.target.value) : undefined }))
            }
            required
          >
            <option value="" disabled>
              Select category…
            </option>
            {categories.map((c) => (
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
            className="border rounded px-2 py-1"
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
          className="ml-2 px-3 py-1 rounded bg-blue-600 text-white disabled:opacity-50"
          disabled={createMut.isPending}
        >
          {createMut.isPending ? "Creating…" : "Create"}
        </button>
        {createMut.isError ? (
          <span className="text-red-600 text-sm">
            {(createMut.error as Error)?.message ?? "Create failed"}
          </span>
        ) : null}
      </form>

      {/* Budgets table */}
      <div className="overflow-x-auto">
        <table className="min-w-[780px] w-full border-collapse">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2 pr-4">Category</th>
              <th className="py-2 pr-4">Limit</th>
              <th className="py-2 pr-4">Period</th>
              <th className="py-2 pr-4">Spent</th>
              <th className="py-2 pr-4">Remaining</th>
              <th className="py-2 pr-4">Used</th>
              <th className="py-2 pr-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {budgets.map((b) => {
              const isEditing = editingId === b.id;

              if (isEditing) {
                return (
                  <tr key={b.id} className="border-b align-top">
                    <td className="py-2 pr-4">
                      <select
                        className="border rounded px-2 py-1"
                        value={editForm.category ?? ""}
                        onChange={(e) =>
                          setEditForm((f) => ({
                            ...f,
                            category: e.target.value ? Number(e.target.value) : undefined,
                          }))
                        }
                        required
                      >
                        <option value="" disabled>
                          Select category…
                        </option>
                        {categories.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.name}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="py-2 pr-4">
                      <input
                        type="number"
                        step="0.01"
                        className="border rounded px-2 py-1 w-28"
                        value={editForm.limit}
                        onChange={(e) => setEditForm((f) => ({ ...f, limit: e.target.value }))}
                        required
                      />
                    </td>
                    <td className="py-2 pr-4">
                      <select
                        className="border rounded px-2 py-1"
                        value={editForm.period}
                        onChange={(e) => setEditForm((f) => ({ ...f, period: e.target.value as "M" | "Y" }))}
                      >
                        <option value="M">Monthly</option>
                        <option value="Y">Yearly</option>
                      </select>
                    </td>
                    <td className="py-2 pr-4">{b.amount_spent ?? "0.00"}</td>
                    <td className="py-2 pr-4">{b.remaining ?? "0.00"}</td>
                    <td className="py-2 pr-4">
                      {b.percent_used != null ? `${b.percent_used.toFixed(1)}%` : "0%"}
                    </td>
                    <td className="py-2 pr-4 space-x-2">
                      <button
                        className="px-2 py-1 rounded bg-green-600 text-white disabled:opacity-50"
                        onClick={() => saveEdit(b.id)}
                        disabled={updateMut.isPending}
                      >
                        {updateMut.isPending ? "Saving…" : "Save"}
                      </button>
                      <button
                        className="px-2 py-1 rounded bg-gray-300"
                        onClick={cancelEdit}
                        disabled={updateMut.isPending}
                      >
                        Cancel
                      </button>
                      {editError && (
                        <div className="text-red-600 text-sm mt-1">{editError}</div>
                      )}
                    </td>
                  </tr>
                );
              }

              return (
                <tr key={b.id} className="border-b">
                  <td className="py-2 pr-4">{catName(b.category)}</td>
                  <td className="py-2 pr-4">{b.limit}</td>
                  <td className="py-2 pr-4">{b.period === "M" ? "Monthly" : "Yearly"}</td>
                  <td className="py-2 pr-4">{b.amount_spent ?? "0.00"}</td>
                  <td className="py-2 pr-4">{b.remaining ?? "0.00"}</td>
                  <td className="py-2 pr-4">
                    {b.percent_used != null ? `${b.percent_used.toFixed(1)}%` : "0%"}
                  </td>
                  <td className="py-2 pr-4 space-x-2">
                    <button
                      className="px-2 py-1 rounded bg-blue-600 text-white"
                      onClick={() => beginEdit(b)}
                    >
                      Edit
                    </button>
                    <button
                      className="px-2 py-1 rounded bg-red-600 text-white disabled:opacity-50"
                      onClick={() => delMut.mutate(b.id)}
                      disabled={delMut.isPending}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              );
            })}
            {budgets.length === 0 && (
              <tr>
                <td className="py-4 text-gray-500" colSpan={7}>
                  No budgets yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
