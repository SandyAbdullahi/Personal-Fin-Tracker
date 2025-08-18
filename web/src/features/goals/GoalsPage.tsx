// src/features/goals/GoalsPage.tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { GoalDTO, GoalPayload } from "./api";
import { listGoals, createGoal, updateGoal, deleteGoal } from "./api";

function pct(saved: string, target: string) {
  const s = Number(saved || 0);
  const t = Number(target || 0);
  if (!t) return 0;
  return Math.min(100, Math.round((s / t) * 100));
}

function Progress({ saved, target }: { saved: string; target: string }) {
  const p = pct(saved, target);
  const barColor =
    p < 50 ? "bg-red-500" : p < 85 ? "bg-yellow-500" : "bg-green-600";
  return (
    <div className="w-40">
      <div className="h-2 bg-gray-200 rounded">
        <div className={`h-2 ${barColor} rounded`} style={{ width: `${p}%` }} />
      </div>
      <div className="text-xs text-gray-600 mt-1">{p}%</div>
    </div>
  );
}

export default function GoalsPage() {
  const qc = useQueryClient();

  const [search, setSearch] = useState("");
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["goals", search],
    queryFn: () => listGoals(search.trim() || undefined),
    keepPreviousData: true,
  });

  const goals: GoalDTO[] = useMemo(() => data?.results ?? [], [data]);

  const [form, setForm] = useState<GoalPayload>({
    name: "",
    target_amount: "",
    current_amount: "",
    target_date: "",
  });

  const createMut = useMutation({
    mutationFn: createGoal,
    onSuccess: () => {
      setForm({ name: "", target_amount: "", current_amount: "", target_date: "" });
      qc.invalidateQueries({ queryKey: ["goals"] });
    },
  });

  const [editingId, setEditingId] = useState<number | null>(null);
  const [edit, setEdit] = useState<Partial<GoalPayload>>({});

  const updateMut = useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: Partial<GoalPayload> }) =>
      updateGoal(id, patch),
    onSuccess: () => {
      setEditingId(null);
      setEdit({});
      qc.invalidateQueries({ queryKey: ["goals"] });
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteGoal(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["goals"] }),
  });

  function startEdit(g: GoalDTO) {
    setEditingId(g.id);
    setEdit({
      name: g.name,
      target_amount: g.target_amount,
      current_amount: g.current_amount,
      target_date: g.target_date,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setEdit({});
  }

  async function quickAdd(g: GoalDTO) {
    const deltaStr = window.prompt(`Add amount to "${g.name}" (e.g. 25.00):`, "0");
    if (!deltaStr) return;
    const delta = Number(deltaStr);
    if (Number.isNaN(delta) || delta <= 0) return;
    const newSaved = (Number(g.current_amount || 0) + delta).toFixed(2);
    await updateMut.mutateAsync({ id: g.id, patch: { current_amount: newSaved } });
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end gap-3">
        <h1 className="text-xl font-bold">Savings Goals</h1>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            refetch();
          }}
          className="ml-auto flex items-center gap-2"
        >
          <input
            className="border rounded px-2 py-1"
            placeholder="Search by name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="px-3 py-1 border rounded" type="submit">
            Search
          </button>
        </form>
      </header>

      <section className="p-3 border rounded space-y-3">
        <h2 className="font-semibold">Create Goal</h2>
        <form
          className="grid grid-cols-1 md:grid-cols-4 gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            createMut.mutate({
              name: form.name.trim(),
              target_amount: form.target_amount || "0",
              current_amount: form.current_amount || "0",
              target_date: form.target_date || null,
            });
          }}
        >
          <input
            className="border rounded px-2 py-1"
            placeholder="Name (e.g. Emergency Fund)"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
          />
          <input
            className="border rounded px-2 py-1"
            placeholder="Target 1000.00"
            type="number"
            step="0.01"
            value={form.target_amount as string}
            onChange={(e) =>
              setForm((f) => ({ ...f, target_amount: e.target.value }))
            }
            required
          />
          <input
            className="border rounded px-2 py-1"
            placeholder="Current 0.00"
            type="number"
            step="0.01"
            value={form.current_amount as string}
            onChange={(e) =>
              setForm((f) => ({ ...f, current_amount: e.target.value }))
            }
          />
          <input
            className="border rounded px-2 py-1"
            type="date"
            value={(form.target_date as string) || ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                target_date: e.target.value || undefined,
              }))
            }
          />
          <div className="md:col-span-4">
            <button
              className="px-3 py-1 border rounded"
              type="submit"
              disabled={createMut.isPending}
            >
              {createMut.isPending ? "Creating…" : "Create Goal"}
            </button>
          </div>
        </form>
        {createMut.isError ? (
          <p className="text-sm text-red-600">
            {(createMut.error as Error).message}
          </p>
        ) : null}
      </section>

      <section>
        {/* loading / error / empty */}
        {/* ... same as before ... */}
      </section>
    </div>
  );
}
