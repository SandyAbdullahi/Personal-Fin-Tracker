// src/features/transfers/TransfersPage.tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createTransfer,
  deleteTransfer,
  listTransfers,
  type TransferDTO,
  type TransferPayload,
} from "./api";
import { getJson } from "../../lib/api";

type CategoryLite = { id: number; name: string };

function useCategories() {
  return useQuery({
    queryKey: ["categories", "all"],
    queryFn: async () => {
      // robust to paginated or non-paginated responses
      const data = await getJson<any>("/api/finance/categories/?page_size=1000");
      if (Array.isArray(data)) return data as CategoryLite[];
      return (data?.results ?? []) as CategoryLite[];
    },
  });
}

function useTransfers() {
  return useQuery({
    queryKey: ["transfers", { page: 1 }],
    queryFn: () => listTransfers({ page: 1 }),
  });
}

const currency = new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: "KES",
});

export default function TransfersPage() {
  // form state
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [form, setForm] = useState<TransferPayload>({
    source_category: 0,
    destination_category: 0,
    amount: "",
    date: today,
    description: "",
  });
  const [error, setError] = useState<string | null>(null);

  const qc = useQueryClient();
  const { data: catData, isLoading: catsLoading } = useCategories();
  const { data: listData, isLoading: listLoading, error: listErr } = useTransfers();

  const categories = catData ?? [];
  const catName = useMemo(() => {
    const map = new Map<number, string>();
    for (const c of categories) map.set(c.id, c.name);
    return (id: number) => map.get(id) ?? `#${id}`;
  }, [categories]);

  const createMut = useMutation({
    mutationFn: createTransfer,
    onSuccess: () => {
      setForm((s) => ({ ...s, amount: "", description: "" }));
      setError(null);
      qc.invalidateQueries({ queryKey: ["transfers"] });
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["summary"] });
    },
    onError: async (e: any) => {
      setError(e?.message ?? "Failed to create transfer");
    },
  });

  const deleteMut = useMutation({
    mutationFn: deleteTransfer,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transfers"] });
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["summary"] });
    },
  });

  const rows: TransferDTO[] = useMemo(() => {
    const d: any = listData;
    if (!d) return [];
    return Array.isArray(d) ? d : d.results ?? [];
  }, [listData]);

  function onChange<K extends keyof TransferPayload>(key: K, val: TransferPayload[K]) {
    setForm((s) => ({ ...s, [key]: val }));
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.source_category || !form.destination_category) {
      setError("Please select both categories.");
      return;
    }
    if (form.source_category === form.destination_category) {
      setError("Source and destination must be different.");
      return;
    }
    if (!form.amount || Number(form.amount) <= 0) {
      setError("Amount must be positive.");
      return;
    }
    createMut.mutate({
      ...form,
      amount: typeof form.amount === "string" ? form.amount.trim() : form.amount,
    });
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold">Transfers</h1>

      {/* Create form */}
      <form onSubmit={onSubmit} className="grid gap-3 max-w-2xl md:grid-cols-5">
        <div className="md:col-span-2">
          <label className="block text-sm mb-1">From (source)</label>
          <select
            className="border rounded px-2 py-1 w-full"
            disabled={catsLoading}
            value={form.source_category || ""}
            onChange={(e) => onChange("source_category", Number(e.target.value))}
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

        <div className="md:col-span-2">
          <label className="block text-sm mb-1">To (destination)</label>
          <select
            className="border rounded px-2 py-1 w-full"
            disabled={catsLoading}
            value={form.destination_category || ""}
            onChange={(e) => onChange("destination_category", Number(e.target.value))}
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
          <label className="block text-sm mb-1">Amount</label>
          <input
            type="number"
            step="0.01"
            className="border rounded px-2 py-1 w-full"
            value={form.amount}
            onChange={(e) => onChange("amount", e.target.value)}
            placeholder="0.00"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">Date</label>
          <input
            type="date"
            className="border rounded px-2 py-1 w-full"
            value={form.date}
            onChange={(e) => onChange("date", e.target.value)}
          />
        </div>

        <div className="md:col-span-5">
          <label className="block text-sm mb-1">Description</label>
          <input
            type="text"
            className="border rounded px-2 py-1 w-full"
            value={form.description ?? ""}
            onChange={(e) => onChange("description", e.target.value)}
            placeholder="Optional memo"
          />
        </div>

        <div className="md:col-span-5">
          <button
            type="submit"
            className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
            disabled={createMut.isPending}
          >
            {createMut.isPending ? "Creating…" : "Create transfer"}
          </button>
          {error && <span className="ml-3 text-red-600 text-sm">{error}</span>}
        </div>
      </form>

      {/* List table */}
      <div className="overflow-x-auto">
        <table className="min-w-[700px] w-full border">
          <thead className="bg-black-50">
            <tr>
              <th className="text-left p-2 border-b">Date</th>
              <th className="text-left p-2 border-b">From</th>
              <th className="text-left p-2 border-b">To</th>
              <th className="text-right p-2 border-b">Amount</th>
              <th className="text-left p-2 border-b">Description</th>
              <th className="text-left p-2 border-b">Actions</th>
            </tr>
          </thead>
          <tbody>
            {listLoading ? (
              <tr>
                <td className="p-3" colSpan={6}>
                  Loading…
                </td>
              </tr>
            ) : listErr ? (
              <tr>
                <td className="p-3 text-red-600" colSpan={6}>
                  {(listErr as Error).message}
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td className="p-3 text-gray-500" colSpan={6}>
                  No transfers yet.
                </td>
              </tr>
            ) : (
              rows.map((t) => (
                <tr key={t.id} className="odd:bg-black even:bg-black-50">
                  <td className="p-2 border-b">{t.date}</td>
                  <td className="p-2 border-b">{catName(t.source_category)}</td>
                  <td className="p-2 border-b">{catName(t.destination_category)}</td>
                  <td className="p-2 border-b text-right">{currency.format(Number(t.amount))}</td>
                  <td className="p-2 border-b">{t.description}</td>
                  <td className="p-2 border-b">
                    <button
                      className="text-red-600 hover:underline disabled:opacity-50"
                      onClick={() => {
                        if (confirm("Delete this transfer?")) {
                          deleteMut.mutate(t.id);
                        }
                      }}
                      disabled={deleteMut.isPending}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
