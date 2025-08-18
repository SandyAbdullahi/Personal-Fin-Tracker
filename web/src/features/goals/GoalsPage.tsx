// src/features/goals/GoalsPage.tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { GoalDTO, GoalPayload } from "./api";
import { listGoals, createGoal, updateGoal, deleteGoal } from "./api";
import toast from "react-hot-toast";

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
      <div className="h-2 bg-black-200 rounded">
        <div className={`h-2 ${barColor} rounded`} style={{ width: `${p}%` }} />
      </div>
      <div className="text-xs text-gray-600 mt-1">{p}%</div>
    </div>
  );
}

export default function GoalsPage() {
  const qc = useQueryClient();

  // ── Search/filter
  const [search, setSearch] = useState("");
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["goals", search],
    queryFn: () => listGoals(search.trim() || undefined),
    keepPreviousData: true,
  });

  // Normalize possible shapes: {results: []} or [] or {data: []}
  const goals: GoalDTO[] = useMemo<GoalDTO[]>(() => {
    if (!data) return [];
    // @ts-ignore – runtime guard
    if (Array.isArray(data)) return data as GoalDTO[];
    // @ts-ignore
    if (Array.isArray(data.results)) return data.results as GoalDTO[];
    // @ts-ignore
    if (Array.isArray(data.data)) return data.data as GoalDTO[];
    return [];
  }, [data]);

  // ── Create form
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
      toast.success("Goal created successfully!");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Failed to create goal");
    },
  });

  // ── Editing
  const [editingId, setEditingId] = useState<number | null>(null);
  const [edit, setEdit] = useState<Partial<GoalPayload>>({});

  const updateMut = useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: Partial<GoalPayload> }) =>
      updateGoal(id, patch),
    onSuccess: () => {
      setEditingId(null);
      setEdit({});
      qc.invalidateQueries({ queryKey: ["goals"] });
      toast.success("Goal updated");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Failed to update goal");
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteGoal(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["goals"] });
      toast.success("Goal deleted");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Failed to delete goal");
    },
  });

  function startEdit(g: GoalDTO) {
    setEditingId(g.id);
    setEdit({
      name: g.name,
      target_amount: g.target_amount,
      current_amount: g.current_amount,
      target_date: g.target_date ?? "",
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

  // Totals
  const totalTarget = useMemo(
    () => goals.reduce((sum, g) => sum + Number(g.target_amount || 0), 0),
    [goals]
  );
  const totalCurrent = useMemo(
    () => goals.reduce((sum, g) => sum + Number(g.current_amount || 0), 0),
    [goals]
  );

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
          <button className="px-3 py-1 border rounded" type="submit" disabled={isFetching}>
            {isFetching ? "Searching…" : "Search"}
          </button>
        </form>
      </header>

      {/* Create */}
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
              target_date: (form.target_date as string) || null,
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
            onChange={(e) => setForm((f) => ({ ...f, target_amount: e.target.value }))}
            required
          />
          <input
            className="border rounded px-2 py-1"
            placeholder="Current 0.00"
            type="number"
            step="0.01"
            value={form.current_amount as string}
            onChange={(e) => setForm((f) => ({ ...f, current_amount: e.target.value }))}
          />
          <input
            className="border rounded px-2 py-1"
            type="date"
            value={(form.target_date as string) || ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                target_date: e.target.value || "",
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
          <p className="text-sm text-red-600">{(createMut.error as Error).message}</p>
        ) : null}
      </section>

      {/* List / table */}
      <section className="border rounded overflow-hidden">
        {isLoading ? (
          <div className="p-4">Loading goals…</div>
        ) : isError ? (
          <div className="p-4 text-red-600">{String(error)}</div>
        ) : goals.length === 0 ? (
          <div className="p-4 text-gray-600">No goals yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-black-50">
              <tr>
                <th className="text-left p-2">Name</th>
                <th className="text-right p-2">Target</th>
                <th className="text-right p-2">Current</th>
                <th className="text-left p-2">Progress</th>
                <th className="text-left p-2">Deadline</th>
                <th className="text-right p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {goals.map((g) => {
                const isEditing = editingId === g.id;
                return (
                  <tr key={g.id} className="border-t">
                    <td className="p-2">
                      {isEditing ? (
                        <input
                          className="border rounded p-1 w-full"
                          value={edit.name ?? ""}
                          onChange={(e) => setEdit((s) => ({ ...s, name: e.target.value }))}
                        />
                      ) : (
                        g.name
                      )}
                    </td>
                    <td className="p-2 text-right">
                      {isEditing ? (
                        <input
                          className="border rounded p-1 w-28 text-right"
                          value={edit.target_amount ?? ""}
                          onChange={(e) =>
                            setEdit((s) => ({ ...s, target_amount: e.target.value }))
                          }
                        />
                      ) : (
                        g.target_amount
                      )}
                    </td>
                    <td className="p-2 text-right">
                      {isEditing ? (
                        <input
                          className="border rounded p-1 w-28 text-right"
                          value={edit.current_amount ?? ""}
                          onChange={(e) =>
                            setEdit((s) => ({ ...s, current_amount: e.target.value }))
                          }
                        />
                      ) : (
                        g.current_amount
                      )}
                    </td>
                    <td className="p-2">
                      <Progress saved={g.current_amount} target={g.target_amount} />
                    </td>
                    <td className="p-2">
                      {isEditing ? (
                        <input
                          type="date"
                          className="border rounded p-1"
                          value={(edit.target_date as string) ?? ""}
                          onChange={(e) =>
                            setEdit((s) => ({ ...s, target_date: e.target.value }))
                          }
                        />
                      ) : (
                        g.target_date ?? "—"
                      )}
                    </td>
                    <td className="p-2 text-right space-x-2">
                      {isEditing ? (
                        <>
                          <button
                            onClick={() =>
                              updateMut.mutate({
                                id: g.id,
                                patch: {
                                  name: edit.name?.trim(),
                                  target_amount: edit.target_amount?.trim(),
                                  current_amount: edit.current_amount?.trim(),
                                  target_date:
                                    (edit.target_date as string)?.trim() || undefined,
                                },
                              })
                            }
                            disabled={updateMut.isPending}
                            className="px-2 py-1 bg-blue-600 text-white rounded disabled:opacity-60"
                          >
                            Save
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="px-2 py-1 bg-black-200 rounded"
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => startEdit(g)}
                            className="px-2 py-1 bg-black-100 rounded"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => quickAdd(g)}
                            className="px-2 py-1 bg-emerald-600 text-white rounded"
                          >
                            Quick add
                          </button>
                          <button
                            onClick={() => {
                              if (confirm(`Delete goal "${g.name}"?`)) {
                                deleteMut.mutate(g.id);
                              }
                            }}
                            disabled={deleteMut.isPending}
                            className="px-2 py-1 bg-red-600 text-white rounded disabled:opacity-60"
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
            <tfoot>
              <tr className="border-t bg-black-50 font-semibold">
                <td className="p-2">Totals</td>
                <td className="p-2 text-right">{totalTarget.toFixed(2)}</td>
                <td className="p-2 text-right">{totalCurrent.toFixed(2)}</td>
                <td className="p-2" />
                <td className="p-2" />
                <td className="p-2" />
              </tr>
            </tfoot>
          </table>
        )}
      </section>
    </div>
  );
}
