// src/features/budgets/BudgetsPage.tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Budget, BudgetList } from "./api";
import { createBudget, deleteBudget, listBudgets } from "./api";

import EditBudgetModal from "./EditBudgetModal";

function pctClass(p: number) {
  if (p >= 100) return "bg-red-500";
  if (p >= 70) return "bg-yellow-500";
  return "bg-green-500";
}

export default function BudgetsPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["budgets"],
    queryFn: () => listBudgets({ ordering: "remaining" }),
  });

  // Create (if you already have a create modal, keep using it — this is an inline quick form)
  const [newCategory, setNewCategory] = useState<number | "">("");
  const [newLimit, setNewLimit] = useState<string>("");
  const [newPeriod, setNewPeriod] = useState<"M" | "Y">("M");

  const createMut = useMutation({
    mutationFn: () =>
      createBudget({
        category: Number(newCategory),
        limit: newLimit,
        period: newPeriod,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      setNewCategory("");
      setNewLimit("");
      setNewPeriod("M");
    },
  });

  // Edit modal state
  const [editOpen, setEditOpen] = useState(false);
  const [selected, setSelected] = useState<Budget | null>(null);

  // Delete
  const delMut = useMutation({
    mutationFn: (id: number) => deleteBudget(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
    },
  });

  const budgets = useMemo(() => (data as BudgetList | undefined)?.results ?? [], [data]);

  if (isLoading) return <div>Loading budgets…</div>;
  if (isError) return <div className="text-red-600">Failed: {(error as Error).message}</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Budgets</h1>

      {/* Quick create row (optional if you already have a modal) */}
      <form
        className="flex flex-wrap gap-2 items-end"
        onSubmit={(e) => {
          e.preventDefault();
          if (newCategory !== "" && newLimit) createMut.mutate();
        }}
      >
        <div className="grid">
          <label className="text-sm">Category ID</label>
          <input
            className="border rounded px-2 py-1 w-32"
            type="number"
            value={newCategory === "" ? "" : Number(newCategory)}
            onChange={(e) =>
              setNewCategory(e.target.value ? Number(e.target.value) : "")
            }
            placeholder="e.g. 3"
            required
          />
        </div>
        <div className="grid">
          <label className="text-sm">Limit</label>
          <input
            className="border rounded px-2 py-1 w-40"
            type="number"
            step="0.01"
            min={0}
            value={newLimit}
            onChange={(e) => setNewLimit(e.target.value)}
            required
          />
        </div>
        <div className="grid">
          <label className="text-sm">Period</label>
          <select
            className="border rounded px-2 py-1"
            value={newPeriod}
            onChange={(e) => setNewPeriod(e.target.value as "M" | "Y")}
          >
            <option value="M">Monthly</option>
            <option value="Y">Yearly</option>
          </select>
        </div>
        <button
          type="submit"
          className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
          disabled={createMut.isLoading || newCategory === "" || !newLimit}
        >
          {createMut.isLoading ? "Creating…" : "Create"}
        </button>
        {createMut.isError ? (
          <div className="text-sm text-red-600">
            {(createMut.error as Error).message}
          </div>
        ) : null}
      </form>

      {/* Budgets table */}
      <div className="overflow-x-auto">
        <table className="min-w-[700px] w-full border">
          <thead className="bg-black-50 text-left">
            <tr>
              <th className="p-2 border-b">ID</th>
              <th className="p-2 border-b">Category</th>
              <th className="p-2 border-b">Limit</th>
              <th className="p-2 border-b">Spent</th>
              <th className="p-2 border-b">Remaining</th>
              <th className="p-2 border-b">Used</th>
              <th className="p-2 border-b">Actions</th>
            </tr>
          </thead>
          <tbody>
            {budgets.map((b) => (
              <tr key={b.id} className="odd:bg-black even:bg-black-50">
                <td className="p-2 border-b">{b.id}</td>
                <td className="p-2 border-b">#{b.category}</td>
                <td className="p-2 border-b">{b.limit}</td>
                <td className="p-2 border-b">{b.amount_spent}</td>
                <td className="p-2 border-b">{b.remaining}</td>
                <td className="p-2 border-b">
                  <div className="flex items-center gap-2">
                    <div className="w-28 h-2 bg-black-200 rounded">
                      <div
                        className={`h-2 rounded ${pctClass(b.percent_used)}`}
                        style={{
                          width: `${Math.min(100, Math.max(0, b.percent_used))}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm">{b.percent_used.toFixed(1)}%</span>
                  </div>
                </td>
                <td className="p-2 border-b">
                  <div className="flex gap-2">
                    <button
                      className="px-2 py-1 text-sm rounded border"
                      onClick={() => {
                        setSelected(b);
                        setEditOpen(true);
                      }}
                    >
                      Edit
                    </button>
                    <button
                      className="px-2 py-1 text-sm rounded border border-red-600 text-red-600"
                      onClick={async () => {
                        if (!confirm("Delete this budget?")) return;
                        delMut.mutate(b.id);
                      }}
                      disabled={delMut.isLoading}
                    >
                      {delMut.isLoading ? "Deleting…" : "Delete"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {!budgets.length && (
              <tr>
                <td className="p-4 text-center text-gray-500" colSpan={7}>
                  No budgets yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <EditBudgetModal
        open={editOpen}
        budget={selected}
        onClose={() => {
          setEditOpen(false);
          setSelected(null);
        }}
      />
    </div>
  );
}
