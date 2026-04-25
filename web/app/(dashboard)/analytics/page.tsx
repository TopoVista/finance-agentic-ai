import { AnalyticsChart } from "@/components/analytics-chart";
import { serverApiFetch } from "@/lib/api";

export default async function AnalyticsPage() {
  const [chartResponse, breakdownResponse] = await Promise.all([
    serverApiFetch<any>("/analytics/chart"),
    serverApiFetch<any>("/analytics/expense-breakdown")
  ]);

  const breakdown = breakdownResponse.data.breakdown ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold">Analytics</h2>
        <p className="mt-1 text-sm text-muted">Trend lines and category concentration for the active period.</p>
      </div>
      <AnalyticsChart data={chartResponse.data.chartData} />
      <section className="rounded-md border border-border bg-panel p-4">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Expense breakdown</h3>
          <span className="text-sm text-muted">${Number(breakdownResponse.data.totalSpent).toFixed(2)} total</span>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {breakdown.map((item: any) => (
            <div key={item.name} className="rounded-md border border-border p-3">
              <div className="text-sm text-muted">{item.name}</div>
              <div className="mt-2 text-xl font-semibold">${Number(item.value).toFixed(2)}</div>
              <div className="mt-1 text-sm text-muted">{item.percentage}% of expenses</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
