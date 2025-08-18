// src/features/budgets/BudgetsPage.tsx
import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listBudgets, createBudget, updateBudget, deleteBudget, type BudgetDTO, type BudgetUpsert } from "./api";
import { listCategories, type CategoryDTO } from "../categories/api";

function formatMoney(x: string | number) {
  const n = typeof x === "string" ? Number(x) : x;
  if (Number.isNaN(n)) return String(x);
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "KES" }).format(n);
}

export default function BudgetsPage() {
  const qc = useQueryClient();

  const { data: budgets = [], isLoading: loadingBudgets, error: budgetsErr } = useQuery({
    queryKey: ["budgets"],
    queryFn: listBudgets,
  });

  const { data: categories = [], isLoading: loadingCats } = useQuery({
    queryKey: ["categories"],
    queryFn: listCategories, // if your API exports fetchCategories, switch import+name
  });

  const categoriesById = useMemo<Record<number, string>>(
    () => Object.fromEntries((categories as CategoryDTO[]).map((c) => [c.id, c.name])),
    [categories]
  );

  // Create
  const [newForm, setNewForm] = useState<BudgetUpsert>({
    category: 0,
    limit: "",
    period: "M",
  });
  const createMut = useMutation({
    mutationFn: createBudget,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setNewForm({ category: 0, limit: "", period: "M" });
    },
  });

  // Inline edit
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<Partial<BudgetUpsert>>({});
  const updateMut = useMutation({
    mutationFn: ({ id, body }: { id: number; body: Partial<BudgetUpsert> }) =>
      updateBudget(id, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setEditingId(null);
      setEditForm({});
    },
  });

  // Delete
  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteBudget(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["budgets"] }),
  });

  if (loadingBudgets || loadingCats) return <div className="p-4">Loading…</div>;
  if (budgetsErr) return <div className="p-4 text-red-600">Failed to load budgets.</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Budgets</h1>

      {/* Create Budget */}
      <form
        className="grid grid-cols-1 sm:grid-cols-5 gap-3 items-end"
        onSubmit={(e) => {
          e.preventDefault();
          if (!newForm.category || !newForm.limit) return;
          createMut.mutate({
            category: Number(newForm.category),
            limit: String(newForm.limit),
            period: newForm.period,
          });
        }}
      >
        <label className="flex flex-col gap-1">
          <span className="text-sm">Category</span>
          <select
            value={newForm.category}
            onChange={(e) => setNewForm((f) => ({ ...f, category: Number(e.target.value) }))}
            className="border rounded p-2"
          >
            <option value={0}>Choose…</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm">Base limit</span>
          <input
            type="number"
            step="0.01"
            value={newForm.limit}
            onChange={(e) => setNewForm((f) => ({ ...f, limit: e.target.value }))}
            className="border rounded p-2"
            placeholder="e.g. 500"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm">Period</span>
          <select
            value={newForm.period}
            onChange={(e) => setNewForm((f) => ({ ...f, period: e.target.value as "M" | "Y" }))}
            className="border rounded p-2"
          >
            <option value="M">Monthly</option>
            <option value="Y">Yearly</option>
          </select>
        </label>

        <button
          type="submit"
          className="bg-blue-600 text-white rounded px-4 py-2 sm:col-span-2"
          disabled={createMut.isPending}
        >
          {createMut.isPending ? "Creating…" : "Create"}
        </button>
      </form>

      {/* Budgets table */}
      <div className="overflow-x-auto">
        <table className="min-w-[900px] w-full border-collapse">
          <thead>
            <tr className="text-left border-b">
              <th className="p-2">Category</th>
              <th className="p-2">Base limit</th>
              <th className="p-2">Reallocated</th>
              <th className="p-2">Effective limit</th>
              <th className="p-2">Spent</th>
              <th className="p-2">Remaining</th>
              <th className="p-2">Used</th>
              <th className="p-2 w-40">Actions</th>
            </tr>
          </thead>
          <tbody>
            {budgets.map((b) => {
              const isEditing = editingId === b.id;

              // ensure numbers for calculations / class decisions
              const limitNum = Number(b.limit);
              const netNum = Number(b.net_transfer);
              const effNum = Number(b.effective_limit);
              const spentNum = Number(b.amount_spent);
              const remNum = Number(b.remaining);
              const usedPct = Number(b.percent_used) || 0;

              return (
                <tr key={b.id} className="border-b align-middle">
                  {/* Category */}
                  <td className="p-2">{categoriesById[b.category] ?? `#${b.category}`}</td>

                  {/* Base limit */}
                  <td className="p-2">
                    {isEditing ? (
                      <input
                        type="number"
                        step="0.01"
                        className="border rounded p-1 w-28"
                        defaultValue={limitNum}
                        onChange={(e) =>
                          setEditForm((f) => ({ ...f, limit: e.target.value }))
                        }
                      />
                    ) : (
                      formatMoney(limitNum)
                    )}
                  </td>

                  {/* Reallocated */}
                  <td className="p-2">
                    <span className={netNum === 0 ? "" : netNum > 0 ? "text-emerald-700" : "text-amber-700"}>
                      {netNum > 0 ? "+" : ""}
                      {formatMoney(netNum)}
                    </span>
                  </td>

                  {/* Effective limit */}
                  <td className="p-2 font-medium">{formatMoney(effNum)}</td>

                  {/* Spent */}
                  <td className="p-2">{formatMoney(spentNum)}</td>

                  {/* Remaining */}
                  <td className="p-2">{formatMoney(remNum)}</td>

                  {/* Used % with tiny bar */}
                  <td className="p-2">
                    <div className="text-xs mb-1">{usedPct.toFixed(0)}%</div>
                    <div className="h-2 bg-gray-200 rounded">
                      <div
                        className={`h-2 rounded ${usedPct > 100 ? "bg-red-500" : "bg-blue-600"}`}
                        style={{ width: `${Math.min(usedPct, 100)}%` }}
                      />
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="p-2 space-x-2">
                    {isEditing ? (
                      <>
                        <button
                          className="px-3 py-1 rounded bg-green-600 text-white"
                          disabled={updateMut.isPending}
                          onClick={() => {
                            if (!editForm.limit) return setEditingId(null);
                            updateMut.mutate({
                              id: b.id,
                              body: { limit: String(editForm.limit) },
                            });
                          }}
                        >
                          Save
                        </button>
                        <button
                          className="px-3 py-1 rounded bg-gray-200"
                          onClick={() => {
                            setEditingId(null);
                            setEditForm({});
                          }}
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          className="px-3 py-1 rounded bg-blue-600 text-white"
                          onClick={() => {
                            setEditingId(b.id);
                            setEditForm({ limit: b.limit });
                          }}
                        >
                          Edit
                        </button>
                        <button
                          className="px-3 py-1 rounded bg-red-600 text-white"
                          disabled={deleteMut.isPending}
                          onClick={() => deleteMut.mutate(b.id)}
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {(createMut.isError || updateMut.isError || deleteMut.isError) && (
        <div className="text-sm text-red-600">
          {(createMut.error as Error)?.message ||
            (updateMut.error as Error)?.message ||
            (deleteMut.error as Error)?.message}
        </div>
      )}
    </div>
  );
}
