// src/features/transactions/TransactionsPage.tsx
import React, { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
  type TransactionDTO,
  type TransactionCreate,
  type Paginated,
} from "./api";
import { listCategories, type Category } from "../categories/api";

type Category = { id: number; name: string };

export default function TransactionsPage() {
  const qc = useQueryClient();

  // UI state
  const [showAdd, setShowAdd] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Queries
  const { data: txPage, isLoading, error } = useQuery({
    queryKey: ["transactions", { page: 1 }],
    queryFn: () => listTransactions({ page: 1 }),
  });

  const { data: categories } = useQuery<Category[]>({
    queryKey: ["categories"],
    queryFn: () => listCategories(),
  });

  const categoryNameById = useMemo(() => {
    const map = new Map<number, string>();
    (categories ?? []).forEach((c) => map.set(c.id, c.name));
    return map;
  }, [categories]);

  // Mutations
  const createMut = useMutation({
    mutationFn: (body: TransactionCreate) => createTransaction(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      setShowAdd(false);
    },
  });

  const updateMut = useMutation({
    mutationFn: (args: { id: number; patch: Partial<TransactionCreate> }) =>
      updateTransaction(args.id, args.patch),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      setEditingId(null);
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteTransaction(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["transactions"] }),
  });

  const rows: TransactionDTO[] = (txPage as Paginated<TransactionDTO> | undefined)?.results ?? [];

  return (
    <div className="space-y-4">
      <header className="flex items-center gap-3">
        <h1 className="text-xl font-semibold">Transactions</h1>
        <button
          className="ml-auto rounded bg-blue-600 text-white px-3 py-1.5 disabled:opacity-50"
          onClick={() => setShowAdd((s) => !s)}
          disabled={createMut.isPending}
        >
          {showAdd ? "Close" : "Add Transaction"}
        </button>
      </header>

      {showAdd && (
        <AddRow
          onCancel={() => setShowAdd(false)}
          onSubmit={(payload) => createMut.mutate(payload)}
          categories={categories ?? []}
          submitting={createMut.isPending}
        />
      )}

      {isLoading && <div>Loading…</div>}
      {error && <div className="text-red-600">Failed to load: {(error as Error).message}</div>}

      {!isLoading && !error && (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 text-sm">
            <thead className="bg-black-50">
              <tr>
                <Th>Date</Th>
                <Th>Description</Th>
                <Th>Category</Th>
                <Th>Type</Th>
                <Th className="text-right">Amount</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr>
                  <td className="p-3 text-gray-500" colSpan={6}>
                    No transactions yet.
                  </td>
                </tr>
              )}

              {rows.map((tx) =>
                editingId === tx.id ? (
                  <EditRow
                    key={tx.id}
                    tx={tx}
                    categories={categories ?? []}
                    saving={updateMut.isPending}
                    onCancel={() => setEditingId(null)}
                    onSave={(patch) => updateMut.mutate({ id: tx.id, patch })}
                  />
                ) : (
                  <tr key={tx.id} className="border-t">
                    <Td>{safeFormatDate(tx.date)}</Td>
                    <Td>{tx.description || "—"}</Td>
                    <Td>{categoryNameById.get(tx.category_id) ?? `#${tx.category_id}`}</Td>
                    <Td>{tx.type === "IN" ? "Income" : "Expense"}</Td>
                    <Td className="text-right">{formatMoney(tx.amount)}</Td>
                    <Td>
                      <div className="flex gap-2">
                        <button
                          className="rounded border px-2 py-1 hover:bg-green-600"
                          onClick={() => setEditingId(tx.id)}
                        >
                          Edit
                        </button>
                        <button
                          className="rounded border px-2 py-1 text-red-600 hover:bg-red-50"
                          onClick={() => {
                            if (confirm("Delete this transaction?")) {
                              deleteMut.mutate(tx.id);
                            }
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    </Td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ---------- small presentational helpers ---------- */
function Th({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <th className={`p-3 text-left font-medium ${className}`}>{children}</th>;
}
function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`p-3 align-top ${className}`}>{children}</td>;
}
function safeFormatDate(d: string | undefined) {
  try {
    if (!d) return "—";
    const dt = new Date(d);
    if (Number.isNaN(dt.getTime())) return d;
    // yyyy-mm-dd
    const yyyy = dt.getFullYear();
    const mm = String(dt.getMonth() + 1).padStart(2, "0");
    const dd = String(dt.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
  } catch {
    return d ?? "—";
  }
}
function formatMoney(v: string | number) {
  const n = typeof v === "string" ? Number(v) : v;
  if (Number.isNaN(n)) return String(v);
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/* ---------- Add row ---------- */
function AddRow({
  onCancel,
  onSubmit,
  categories,
  submitting,
}: {
  onCancel: () => void;
  onSubmit: (payload: TransactionCreate) => void;
  categories: Category[];
  submitting: boolean;
}) {
  const [form, setForm] = useState<TransactionCreate>({
    category_id: categories[0]?.id ?? 0,
    type: "EX",
    amount: "",
    date: new Date().toISOString().slice(0, 10),
    description: "",
  });

  return (
    <div className="rounded border p-3 space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        <Select
          label="Category"
          value={form.category_id}
          onChange={(v) => setForm({ ...form, category_id: Number(v) })}
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
        />
        <Select
          label="Type"
          value={form.type}
          onChange={(v) => setForm({ ...form, type: v as "IN" | "EX" })}
          options={[
            { value: "EX", label: "Expense" },
            { value: "IN", label: "Income" },
          ]}
        />
        <Input
          label="Amount"
          type="number"
          value={String(form.amount)}
          onChange={(v) => setForm({ ...form, amount: v })}
        />
        <Input
          label="Date"
          type="date"
          value={form.date}
          onChange={(v) => setForm({ ...form, date: v })}
        />
        <Input
          label="Description"
          value={form.description ?? ""}
          onChange={(v) => setForm({ ...form, description: v })}
        />
      </div>
      <div className="flex gap-2">
        <button
          className="rounded bg-blue-600 text-white px-3 py-1.5 disabled:opacity-50"
          onClick={() => onSubmit(form)}
          disabled={submitting}
        >
          {submitting ? "Saving…" : "Save"}
        </button>
        <button className="rounded border px-3 py-1.5" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}

/* ---------- Edit row ---------- */
function EditRow({
  tx,
  categories,
  onCancel,
  onSave,
  saving,
}: {
  tx: TransactionDTO;
  categories: Category[];
  onCancel: () => void;
  onSave: (patch: Partial<TransactionCreate>) => void;
  saving: boolean;
}) {
  const [form, setForm] = useState<Partial<TransactionCreate>>({
    category_id: tx.category_id,
    type: tx.type,
    amount: String(tx.amount),
    date: tx.date,
    description: tx.description ?? "",
  });

  return (
    <tr className="border-t bg-yellow-50/40">
      <Td>
        <Input
          label={null}
          type="date"
          value={form.date ?? ""}
          onChange={(v) => setForm({ ...form, date: v })}
          compact
        />
      </Td>
      <Td>
        <Input
          label={null}
          value={form.description ?? ""}
          onChange={(v) => setForm({ ...form, description: v })}
          compact
        />
      </Td>
      <Td>
        <Select
          label={null}
          value={form.category_id ?? tx.category_id}
          onChange={(v) => setForm({ ...form, category_id: Number(v) })}
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
          compact
        />
      </Td>
      <Td>
        <Select
          label={null}
          value={form.type ?? tx.type}
          onChange={(v) => setForm({ ...form, type: v as "IN" | "EX" })}
          options={[
            { value: "EX", label: "Expense" },
            { value: "IN", label: "Income" },
          ]}
          compact
        />
      </Td>
      <Td className="text-right">
        <Input
          label={null}
          type="number"
          value={String(form.amount ?? tx.amount)}
          onChange={(v) => setForm({ ...form, amount: v })}
          compact
        />
      </Td>
      <Td>
        <div className="flex gap-2">
          <button
            className="rounded bg-blue-600 text-white px-3 py-1.5 disabled:opacity-50"
            onClick={() => onSave(form)}
            disabled={saving}
          >
            {saving ? "Saving…" : "Save"}
          </button>
          <button className="rounded border px-3 py-1.5" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </Td>
    </tr>
  );
}

/* ---------- tiny form inputs ---------- */
function Input({
  label,
  type = "text",
  value,
  onChange,
  compact = false,
}: {
  label: string | null;
  type?: string;
  value: string | number;
  onChange: (v: string) => void;
  compact?: boolean;
}) {
  return (
    <label className={`flex flex-col ${compact ? "" : "gap-1"}`}>
      {label !== null && <span className="text-xs text-gray-600">{label}</span>}
      <input
        className="border rounded px-2 py-1 w-full"
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
function Select({
  label,
  value,
  onChange,
  options,
  compact = false,
}: {
  label: string | null;
  value: string | number;
  onChange: (v: string) => void;
  options: { value: string | number; label: string }[];
  compact?: boolean;
}) {
  return (
    <label className={`flex flex-col ${compact ? "" : "gap-1"}`}>
      {label !== null && <span className="text-xs text-gray-600">{label}</span>}
      <select
        className="border rounded px-2 py-1 w-full bg-yellow"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={String(o.value)} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
