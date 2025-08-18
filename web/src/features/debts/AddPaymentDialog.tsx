// src/features/debts/AddPaymentDialog.tsx
import { useEffect, useState } from "react";
import type { DebtDTO, PaymentPayload } from "./api";

type Props = {
  debt: DebtDTO | null;
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: PaymentPayload) => Promise<void> | void;
};

export default function AddPaymentDialog({ debt, open, onClose, onSubmit }: Props) {
  const [amount, setAmount] = useState<string>("");
  const [date, setDate] = useState<string>("");
  const [memo, setMemo] = useState<string>("");

  useEffect(() => {
    if (open && debt) {
      setAmount("");
      setDate(new Date().toISOString().slice(0, 10));
      setMemo("");
    }
  }, [open, debt]);

  if (!open || !debt) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-black rounded shadow p-4 w-full max-w-md">
        <h3 className="font-semibold text-lg mb-3">Add Payment – {debt.name}</h3>

        <form
          className="space-y-3"
          onSubmit={async (e) => {
            e.preventDefault();
            await onSubmit({
              debt: debt.id,
              amount: amount || "0",
              date: date || new Date().toISOString().slice(0, 10),
              memo: memo || undefined,
            });
            onClose();
          }}
        >
          <div>
            <label className="block text-sm mb-1">Amount</label>
            <input
              className="border rounded px-2 py-1 w-full"
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Date</label>
            <input
              className="border rounded px-2 py-1 w-full"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Memo (optional)</label>
            <input
              className="border rounded px-2 py-1 w-full"
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="e.g. Extra payment"
            />
          </div>

          <div className="flex gap-2 justify-end pt-2">
            <button
              type="button"
              className="px-3 py-1 border rounded"
              onClick={onClose}
            >
              Cancel
            </button>
            <button className="px-3 py-1 border rounded bg-black text-white" type="submit">
              Record Payment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
