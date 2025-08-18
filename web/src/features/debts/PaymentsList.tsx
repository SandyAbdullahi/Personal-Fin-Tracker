// src/features/debts/PaymentsList.tsx
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createPayment, deletePayment, listPayments } from "./api";
import type { PaymentDTO } from './api.ts'
import { useState } from "react";
import toast from "react-hot-toast";

export default function PaymentsList({ debtId }: { debtId: number }) {
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["payments", debtId],
    queryFn: () => listPayments(debtId),
  });
  const payments: PaymentDTO[] = data?.results ?? [];

  const [amount, setAmount] = useState("");
  const [date, setDate] = useState<string>(() => new Date().toISOString().slice(0, 10));
  const [memo, setMemo] = useState("");

  const addMut = useMutation({
    mutationFn: () => createPayment({ debt: debtId, amount, date, memo: memo || undefined }),
    onSuccess: () => {
      setAmount(""); setMemo("");
      qc.invalidateQueries({ queryKey: ["payments", debtId] });
      qc.invalidateQueries({ queryKey: ["debts"] }); // balances change
      toast.success("Payment added");
    },
    onError: (e: any) => toast.error(e.message ?? "Failed to add payment"),
  });

  const delMut = useMutation({
    mutationFn: (id: number) => deletePayment(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["payments", debtId] });
      qc.invalidateQueries({ queryKey: ["debts"] });
      toast.success("Payment deleted");
    },
  });

  if (isLoading) return <div className="text-sm text-gray-500 p-2">Loading payments…</div>;
  if (isError)   return <div className="text-sm text-red-600 p-2">Failed to load payments</div>;

  return (
    <div className="border rounded p-3 space-y-3 bg-black-50">
      {/* Add Payment */}
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => { e.preventDefault(); addMut.mutate(); }}
      >
        <input
          className="border rounded px-2 py-1 w-28"
          type="number" step="0.01" min="0"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
        <input
          className="border rounded px-2 py-1"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />
        <input
          className="border rounded px-2 py-1 flex-1"
          placeholder="Memo (optional)"
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
        />
        <button className="px-3 py-1 border rounded" type="submit" disabled={addMut.isPending}>
          {addMut.isPending ? "Adding…" : "Add Payment"}
        </button>
      </form>

      {/* List */}
      {payments.length === 0 ? (
        <div className="text-sm text-gray-500">No payments yet.</div>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-1 pr-2">Date</th>
              <th className="py-1 pr-2">Amount</th>
              <th className="py-1 pr-2">Memo</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id} className="border-b last:border-0">
                <td className="py-1 pr-2">{p.date}</td>
                <td className="py-1 pr-2">{p.amount}</td>
                <td className="py-1 pr-2">{p.memo ?? ""}</td>
                <td className="py-1 pr-2 text-right">
                  <button
                    className="text-red-600 hover:underline"
                    onClick={() => delMut.mutate(p.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
