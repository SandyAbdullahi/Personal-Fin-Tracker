// src/features/debts/DebtsPage.tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import {
  listDebts,
  createDebt,
  updateDebt,
  deleteDebt,
  createPayment,
  type DebtDTO,
  type DebtPayload,
} from "./api";

import AddPaymentDialog from "./AddPaymentDialog";
import PaymentsList from "./PaymentsList";

export default function DebtsPage() {
  const qc = useQueryClient();

  // ── Load debts ──────────────────────────────────────────────────────────
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["debts"],
    queryFn: listDebts,
    staleTime: 15_000,
  });
  const debts: DebtDTO[] = useMemo(() => data?.results ?? [], [data]);

  // ── Create debt form state ──────────────────────────────────────────────
  const [form, setForm] = useState<DebtPayload>({
    name: "",
    principal: "",
    interest_rate: "",
    minimum_payment: "",
    opened_date: "",
  });

  // ── Mutations: create / update / delete debts ───────────────────────────
  const createMut = useMutation({
    mutationFn: createDebt,
    onSuccess: () => {
      setForm({
        name: "",
        principal: "",
        interest_rate: "",
        minimum_payment: "",
        opened_date: "",
      });
      qc.invalidateQueries({ queryKey: ["debts"] });
      toast.success("Debt created");
    },
    onError: (e: any) => toast.error(e?.message ?? "Create failed"),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: Partial<DebtPayload> }) =>
      updateDebt(id, patch),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["debts"] });
      toast.success("Debt updated");
    },
    onError: (e: any) => toast.error(e?.message ?? "Update failed"),
  });

  const deleteMut = useMutation({
    mutationFn: deleteDebt,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["debts"] });
      toast.success("Debt deleted");
    },
    onError: (e: any) => toast.error(e?.message ?? "Delete failed"),
  });

  // ── Payments modal (optional, kept from your version) ───────────────────
  const [payDebt, setPayDebt] = useState<DebtDTO | null>(null);
  const paymentMut = useMutation({
    mutationFn: createPayment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["debts"] });
      toast.success("Payment recorded");
    },
    onError: (e: any) => toast.error(e?.message ?? "Payment failed"),
  });

  // ── Expand/collapse a debt's payments table ─────────────────────────────
  const [openId, setOpenId] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      <header className="flex items-end gap-3">
        <h1 className="text-xl font-bold">Debts & Payments</h1>
        <button className="ml-auto px-3 py-1 border rounded" onClick={() => refetch()}>
          Refresh
        </button>
      </header>

      {/* Create Debt */}
      <section className="p-3 border rounded space-y-3">
        <h2 className="font-semibold">Create Debt</h2>
        <form
          className="grid grid-cols-1 md:grid-cols-5 gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            createMut.mutate({
              name: form.name.trim(),
              principal: form.principal || "0",
              interest_rate: form.interest_rate || "0",
              minimum_payment: form.minimum_payment || "0",
              opened_date: form.opened_date || null,
            });
          }}
        >
          <input
            className="border rounded px-2 py-1"
            placeholder="Name (Credit Card A)"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
          />
          <input
            className="border rounded px-2 py-1"
            placeholder="Principal 5000.00"
            type="number"
            step="0.01"
            value={form.principal}
            onChange={(e) => setForm((f) => ({ ...f, principal: e.target.value }))}
            required
          />
          <input
            className="border rounded px-2 py-1"
            placeholder="APR % e.g. 17.99"
            type="number"
            step="0.01"
            value={form.interest_rate}
            onChange={(e) => setForm((f) => ({ ...f, interest_rate: e.target.value }))}
            required
          />
          <input
            className="border rounded px-2 py-1"
            placeholder="Min payment 50.00"
            type="number"
            step="0.01"
            value={form.minimum_payment}
            onChange={(e) =>
              setForm((f) => ({ ...f, minimum_payment: e.target.value }))
            }
            required
          />
          <input
            className="border rounded px-2 py-1"
            type="date"
            value={form.opened_date ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, opened_date: e.target.value }))}
          />
          <div className="md:col-span-5">
            <button className="px-3 py-1 border rounded" disabled={createMut.isPending}>
              {createMut.isPending ? "Creating…" : "Create Debt"}
            </button>
          </div>
        </form>
      </section>

      {/* Debts Table */}
      <section className="overflow-x-auto">
        {isLoading ? (
          <p className="text-sm text-black-600 p-2">Loading…</p>
        ) : isError ? (
          <p className="text-sm text-red-600 p-2">Failed to load debts.</p>
        ) : debts.length === 0 ? (
          <p className="text-sm text-black-600 p-2">No debts yet.</p>
        ) : (
          <table className="min-w-[820px] w-full border">
            <thead className="bg-black-50">
              <tr className="[&>th]:p-2 [&>th]:text-left">
                <th>Name</th>
                <th>Principal</th>
                <th>Balance</th>
                <th>APR %</th>
                <th>Min Pay</th>
                <th className="w-64">Actions</th>
              </tr>
            </thead>

            {/* For valid markup, group each row + details in its own <tbody> */}
            {debts.map((d) => (
              <tbody key={d.id}>
                <DebtRow
                  d={d}
                  onEdit={(patch) => updateMut.mutate({ id: d.id, patch })}
                  onDelete={() => deleteMut.mutate(d.id)}
                  onAddPayment={() => setPayDebt(d)}
                  onToggle={() => setOpenId((cur) => (cur === d.id ? null : d.id))}
                  isOpen={openId === d.id}
                />
                {openId === d.id ? (
                  <tr>
                    <td colSpan={6} className="p-2 bg-black-50">
                      <PaymentsList debtId={d.id} />
                    </td>
                  </tr>
                ) : null}
              </tbody>
            ))}
          </table>
        )}
      </section>

      {/* Payment modal (kept) */}
      <AddPaymentDialog
        debt={payDebt}
        open={!!payDebt}
        onClose={() => setPayDebt(null)}
        onSubmit={async (payload) => {
          await paymentMut.mutateAsync(payload);
          setPayDebt(null);
        }}
      />
    </div>
  );
}

function DebtRow({
  d,
  onEdit,
  onDelete,
  onAddPayment,
  onToggle,
  isOpen,
}: {
  d: DebtDTO;
  onEdit: (patch: Partial<DebtPayload>) => void;
  onDelete: () => void;
  onAddPayment: () => void;
  onToggle: () => void;
  isOpen: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [edit, setEdit] = useState<Partial<DebtPayload>>({
    name: d.name,
    principal: d.principal,
    interest_rate: d.interest_rate,
    minimum_payment: d.minimum_payment,
  });

  return (
    <tr className="[&>td]:p-2 border-t align-top">
      <td>
        {editing ? (
          <input
            className="border rounded px-1 py-0.5"
            value={edit.name ?? ""}
            onChange={(e) => setEdit((p) => ({ ...p, name: e.target.value }))}
          />
        ) : (
          d.name
        )}
      </td>
      <td>
        {editing ? (
          <input
            className="border rounded px-1 py-0.5"
            type="number"
            step="0.01"
            value={edit.principal ?? ""}
            onChange={(e) => setEdit((p) => ({ ...p, principal: e.target.value }))}
          />
        ) : (
          d.principal
        )}
      </td>
      <td>{d.balance}</td>
      <td>
        {editing ? (
          <input
            className="border rounded px-1 py-0.5"
            type="number"
            step="0.01"
            value={edit.interest_rate ?? ""}
            onChange={(e) => setEdit((p) => ({ ...p, interest_rate: e.target.value }))}
          />
        ) : (
          d.interest_rate
        )}
      </td>
      <td>
        {editing ? (
          <input
            className="border rounded px-1 py-0.5"
            type="number"
            step="0.01"
            value={edit.minimum_payment ?? ""}
            onChange={(e) =>
              setEdit((p) => ({ ...p, minimum_payment: e.target.value }))
            }
          />
        ) : (
          d.minimum_payment
        )}
      </td>
      <td className="flex flex-wrap gap-2">
        {editing ? (
          <>
            <button
              className="px-2 py-1 border rounded"
              onClick={() => {
                onEdit(edit);
                setEditing(false);
              }}
            >
              Save
            </button>
            <button className="px-2 py-1 border rounded" onClick={() => setEditing(false)}>
              Cancel
            </button>
          </>
        ) : (
          <>
            <button className="px-2 py-1 border rounded" onClick={() => setEditing(true)}>
              Edit
            </button>
            <button className="px-2 py-1 border rounded" onClick={onAddPayment}>
              Add Payment
            </button>
            <button className="px-2 py-1 border rounded" onClick={onToggle}>
              {isOpen ? "Hide payments" : "Show payments"}
            </button>
            <button
              className="px-2 py-1 border rounded text-red-600"
              onClick={onDelete}
            >
              Delete
            </button>
          </>
        )}
      </td>
    </tr>
  );
}
