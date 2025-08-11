import { useState } from "react";
import { useTransactions } from "./useTransactions";

export default function TransactionsPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useTransactions(
    search ? { search } : undefined as any
  );

  if (isLoading) return <p>Loading…</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Transactions</h1>
      <input
        className="border px-3 py-2 rounded w-full max-w-md"
        placeholder="Search description…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <table className="w-full border">
        <thead>
          <tr className="bg-black-50 text-left">
            <th className="p-2">Date</th>
            <th className="p-2">Category</th>
            <th className="p-2">Type</th>
            <th className="p-2">Amount</th>
            <th className="p-2">Description</th>
          </tr>
        </thead>
        <tbody>
          {data.results?.map((t: any) => (
            <tr key={t.id} className="border-t">
              <td className="p-2">{t.date}</td>
              <td className="p-2">{t.category_id}</td>
              <td className="p-2">{t.type}</td>
              <td className="p-2">{t.amount}</td>
              <td className="p-2">{t.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
