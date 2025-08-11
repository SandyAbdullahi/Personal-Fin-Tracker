// src/features/budgets/BudgetsPage.tsx
import { useMemo, useState } from "react";
import { useBudgets } from "./api";
import { useCategories } from "../categories/api";
import CreateBudgetModal from "./CreateBudgetModal";

function pctClass(p: number) {
  if (p >= 100) return "bg-red-600";
  if (p >= 75) return "bg-orange-500";
  if (p >= 50) return "bg-yellow-500";
  return "bg-green-600";
}

export default function BudgetsPage() {
  const [open, setOpen] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<number | "">("");
  const [ordering, setOrdering] = useState<"-created" | "remaining" | "-remaining" | "percent_used" | "-percent_used">("-created");

  const { data, isLoading, isError, error } = useBudgets({
    category: categoryFilter ? Number(categoryFilter) : undefined,
    ordering,
  });
  const { data: cats } = useCategories();

  const catMap = useMemo(() => {
    const m = new Map<number, string>();
    cats?.results?.forEach((c) => m.set(c.id, c.name));
    return m;
  }, [cats]);

  if (isError) {
    return <div className="text-red-600">Failed to load budgets: {(error as Error)?.message}</div>;
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <h1 className="text-xl font-bold">Budgets</h1>
        <div className="ml-auto flex gap-2">
          <select
            className="border rounded px-2 py-1"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value ? Number(e.target.value) : "")}
          >
            <option value="">All categories</option>
            {cats?.results?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

            <select
              className="border rounded px-2 py-1"
              value={ordering}
              onChange={(e) => setOrdering(e.target.value as any)}
            >
              <option value="-created">Newest</option>
              <option value="remaining">Remaining ↑</option>
              <option value="-remaining">Remaining ↓</option>
              <option value="percent_used">Usage % ↑</option>
              <option value="-percent_used">Usage % ↓</option>
            </select>

          <button className="px-3 py-1 rounded bg-blue-600 text-white" onClick={() => setOpen(true)}>
            New Budget
          </button>
        </div>
      </div>

      {isLoading ? (
        <div>Loading…</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-2">Category</th>
                <th className="py-2 pr-2">Limit</th>
                <th className="py-2 pr-2">Spent</th>
                <th className="py-2 pr-2">Remaining</th>
                <th className="py-2 pr-2 w-64">Progress</th>
              </tr>
            </thead>
            <tbody>
              {data?.results?.map((b) => {
                const p = Math.min(Math.max(b.percent_used ?? 0, 0), 200); // clamp
                const catName = catMap.get(b.category) ?? `#${b.category}`;
                return (
                  <tr key={b.id} className="border-b">
                    <td className="py-2 pr-2">{catName}</td>
                    <td className="py-2 pr-2">KES {Number(b.limit).toLocaleString()}</td>
                    <td className="py-2 pr-2">KES {Number(b.amount_spent).toLocaleString()}</td>
                    <td className="py-2 pr-2">KES {Number(b.remaining).toLocaleString()}</td>
                    <td className="py-2 pr-2">
                      <div className="w-full h-3 bg-gray-200 rounded">
                        <div
                          className={`h-3 rounded ${pctClass(p)}`}
                          style={{ width: `${Math.min(p, 100)}%` }}
                          title={`${p.toFixed(1)}%`}
                        />
                      </div>
                      <div className="text-[11px] text-gray-600 mt-1">{p.toFixed(1)}%</div>
                    </td>
                  </tr>
                );
              })}
              {data?.results?.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-gray-500">
                    No budgets yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <CreateBudgetModal open={open} onClose={() => setOpen(false)} />
    </div>
  );
}
