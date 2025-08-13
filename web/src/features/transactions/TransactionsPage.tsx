// src/features/transactions/TransactionsPage.tsx
import { useMemo, useState } from "react";
import { useTransactions } from "./api";
import AddTransactionForm from "./AddTransactionForm";

export default function TransactionsPage() {
  const [search, setSearch] = useState("");
  const params = useMemo(() => (search ? { search } : undefined), [search]);
  const { data, isLoading, isError, error } = useTransactions(params);

  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Transactions</h1>

      {/* New: quick-create form */}
      <AddTransactionForm onCreated={() => {/* no-op; list auto refreshes via invalidate */}} />

      <div className="mb-3">
        <input
          className="border rounded px-2 py-1"
          placeholder="Search description…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading && <div>Loading…</div>}
      {isError && <div className="text-red-600">{(error as Error)?.message}</div>}

      {data && (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">ID</th>
              <th className="text-left p-2">Category ID</th>
              <th className="text-left p-2">Type</th>
              <th className="text-left p-2">Amount</th>
              <th className="text-left p-2">Date</th>
              <th className="text-left p-2">Description</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((t) => (
              <tr key={t.id} className="border-b">
                <td className="p-2">{t.id}</td>
                <td className="p-2">{t.category_id}</td>
                <td className="p-2">{t.type}</td>
                <td className="p-2">{t.amount}</td>
                <td className="p-2">{t.date}</td>
                <td className="p-2">{t.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
