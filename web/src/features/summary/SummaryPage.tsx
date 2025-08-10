import { useSummary } from "./useSummary";

export default function SummaryPage() {
  const { data, isLoading, error } = useSummary();
  if (isLoading) return <p>Loading…</p>;
  if (error) return <p>Failed to load summary</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border rounded">
          <div className="text-sm text-gray-500">Income total</div>
          <div className="text-2xl">{data.income_total}</div>
        </div>
        <div className="p-4 border rounded">
          <div className="text-sm text-gray-500">Expense total</div>
          <div className="text-2xl">{data.expense_total}</div>
        </div>
      </div>

      <div>
        <h2 className="font-medium mb-2">By category</h2>
        <ul className="space-y-1">
          {data.by_category.map((row: any) => (
            <li key={row.name} className="flex justify-between border-b py-1">
              <span>{row.name}</span>
              <span>{row.total}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
