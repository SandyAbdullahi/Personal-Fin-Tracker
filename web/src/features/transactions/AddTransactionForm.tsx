// src/features/transactions/AddTransactionForm.tsx
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createTransaction } from "./api";
import type { TransactionPayload } from "./api";          // 👈 type-only
import { fetchCategories } from "../categories/api";

type Props = { onCreated?: () => void };

export default function AddTransactionForm({ onCreated }: Props) {
  const qc = useQueryClient();

  const [loadingCats, setLoadingCats] = useState(true);
  const [cats, setCats] = useState<{ id: number; name: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<TransactionPayload>({
    category_id: 0,
    amount: "",
    type: "EX",
    date: new Date().toISOString().slice(0, 10),
    description: "",
  });

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const data = await fetchCategories();
        if (!alive) return;
        setCats(data);
        if (data.length && form.category_id === 0) {
          setForm((f) => ({ ...f, category_id: data[0].id }));
        }
      } catch (e: any) {
        setError(e?.message ?? "Failed to load categories");
      } finally {
        setLoadingCats(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const { mutateAsync, isPending } = useMutation({
    mutationFn: createTransaction,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      onCreated?.();
    },
  });

  const canSubmit = useMemo(() => {
    return (
      form.category_id > 0 &&
      !!form.amount &&
      (form.type === "IN" || form.type === "EX") &&
      !!form.date
    );
  }, [form]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await mutateAsync({
        ...form,
        amount: String(form.amount),
        category_id: Number(form.category_id),
      });
      setForm((f) => ({ ...f, amount: "", description: "" }));
    } catch (e: any) {
      setError(e?.message ?? "Create failed");
    }
  }

  if (loadingCats) return <div className="text-sm text-gray-500">Loading categories…</div>;
  if (error) return <div className="text-sm text-red-600">{error}</div>;

  return (
    <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3 p-3 border rounded mb-4">
      <div className="flex flex-col">
        <label className="text-sm mb-1">Category</label>
        <select
          className="border rounded px-2 py-1"
          value={form.category_id}
          onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })}
        >
          {cats.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col">
        <label className="text-sm mb-1">Type</label>
        <select
          className="border rounded px-2 py-1"
          value={form.type}
          onChange={(e) => setForm({ ...form, type: e.target.value as "IN" | "EX" })}
        >
          <option value="EX">Expense</option>
          <option value="IN">Income</option>
        </select>
      </div>

      <div className="flex flex-col">
        <label className="text-sm mb-1">Amount</label>
        <input
          type="number"
          step="0.01"
          className="border rounded px-2 py-1"
          value={form.amount as string | number}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
          placeholder="0.00"
          required
        />
      </div>

      <div className="flex flex-col">
        <label className="text-sm mb-1">Date</label>
        <input
          type="date"
          className="border rounded px-2 py-1"
          value={form.date}
          onChange={(e) => setForm({ ...form, date: e.target.value })}
          required
        />
      </div>

      <div className="flex-1 flex flex-col min-w-[200px]">
        <label className="text-sm mb-1">Description (optional)</label>
        <input
          type="text"
          className="border rounded px-2 py-1"
          value={form.description ?? ""}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          placeholder="e.g. Groceries"
        />
      </div>

      <button
        type="submit"
        disabled={!canSubmit || isPending}
        className="px-3 py-2 rounded bg-blue-600 text-white disabled:bg-blue-300"
      >
        {isPending ? "Saving…" : "Add Transaction"}
      </button>
    </form>
  );
}
