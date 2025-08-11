// src/features/summary/SummaryPage.tsx
import { useQuery } from "@tanstack/react-query";
import { getJson } from "../../lib/api";

type CategoryRow = { name: string; total: string | number };
type GoalRow = {
  id: number;
  name: string;
  target: string | number;
  saved: string | number;
  percent: number;
  deadline: string | null;
};

type SummaryResponse = {
  income_total: string | number;
  expense_total: string | number;
  by_category: CategoryRow[];
  goals: GoalRow[];
};

const fetchSummary = () => getJson<SummaryResponse>("/api/finance/summary/");

const money = new Intl.NumberFormat("en-KE", {
  style: "currency",
  currency: "KES",
  maximumFractionDigits: 2,
});

export default function SummaryPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["summary"],
    queryFn: fetchSummary,
  });

  if (isLoading) return <div>Loading…</div>;
  if (error || !data) return <div>Failed to load summary</div>;

  const income = Number(data.income_total ?? 0);
  const expenses = Number(data.expense_total ?? 0);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-xl font-bold mb-2">Summary</h1>
        <div className="flex gap-6">
          <div>Income: <strong>{money.format(income)}</strong></div>
          <div>Expenses: <strong>{money.format(expenses)}</strong></div>
          <div>
            Net:{" "}
            <strong className={income - expenses >= 0 ? "text-green-700" : "text-red-700"}>
              {money.format(income - expenses)}
            </strong>
          </div>
        </div>
      </header>

      <div className="grid gap-8 md:grid-cols-2">
        {/* By Category */}
        <section>
          <h2 className="font-semibold mb-3">By Category</h2>
          <div className="overflow-x-auto border rounded">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2">Category</th>
                  <th className="text-right px-3 py-2">Total</th>
                </tr>
              </thead>
              <tbody>
                {data.by_category.length === 0 ? (
                  <tr>
                    <td className="px-3 py-3 text-gray-500" colSpan={2}>
                      No category data yet.
                    </td>
                  </tr>
                ) : (
                  data.by_category.map((row, i) => (
                    <tr key={`${row.name}-${i}`} className="border-t">
                      <td className="px-3 py-2">{row.name}</td>
                      <td className="px-3 py-2 text-right">
                        {money.format(Number(row.total ?? 0))}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Goals */}
        <section>
          <h2 className="font-semibold mb-3">Goals</h2>
          <div className="overflow-x-auto border rounded">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2">Name</th>
                  <th className="text-right px-3 py-2">Target</th>
                  <th className="text-right px-3 py-2">Saved</th>
                  <th className="text-right px-3 py-2">% Complete</th>
                  <th className="text-left px-3 py-2">Deadline</th>
                </tr>
              </thead>
              <tbody>
                {data.goals.length === 0 ? (
                  <tr>
                    <td className="px-3 py-3 text-gray-500" colSpan={5}>
                      No goals yet.
                    </td>
                  </tr>
                ) : (
                  data.goals.map((g) => (
                    <tr key={g.id} className="border-t">
                      <td className="px-3 py-2">{g.name}</td>
                      <td className="px-3 py-2 text-right">{money.format(Number(g.target ?? 0))}</td>
                      <td className="px-3 py-2 text-right">{money.format(Number(g.saved ?? 0))}</td>
                      <td className="px-3 py-2 text-right">
                        {Number.isFinite(g.percent) ? g.percent.toFixed(1) : "0.0"}%
                      </td>
                      <td className="px-3 py-2">
                        {g.deadline ? new Date(g.deadline).toLocaleDateString() : "—"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
