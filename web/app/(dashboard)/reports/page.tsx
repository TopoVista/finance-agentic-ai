import { serverApiFetch } from "@/lib/api";

export default async function ReportsPage() {
  const response = await serverApiFetch<any>("/report/all?pageSize=20&pageNumber=1");
  const setting = response.reportSetting;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold">Reports</h2>
        <p className="mt-1 text-sm text-muted">Delivery settings and generated report history.</p>
      </div>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-md border border-border bg-panel p-4">
          <div className="text-sm text-muted">Schedule</div>
          <div className="mt-2 text-xl font-semibold">{setting?.frequency ?? "MONTHLY"}</div>
        </div>
        <div className="rounded-md border border-border bg-panel p-4">
          <div className="text-sm text-muted">Enabled</div>
          <div className="mt-2 text-xl font-semibold">{setting?.isEnabled ? "Yes" : "No"}</div>
        </div>
        <div className="rounded-md border border-border bg-panel p-4">
          <div className="text-sm text-muted">Next report date</div>
          <div className="mt-2 text-xl font-semibold">
            {setting?.nextReportDate ? new Date(setting.nextReportDate).toLocaleDateString() : "Not scheduled"}
          </div>
        </div>
      </section>
      <section className="rounded-md border border-border bg-panel p-4">
        <h3 className="text-lg font-semibold">History</h3>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-muted">
                <th className="px-2 py-2">Period</th>
                <th className="px-2 py-2">Status</th>
                <th className="px-2 py-2">Sent</th>
              </tr>
            </thead>
            <tbody>
              {response.reports.map((report: any) => (
                <tr key={report.id} className="border-b border-border/60">
                  <td className="px-2 py-3">{report.period}</td>
                  <td className="px-2 py-3">{report.status}</td>
                  <td className="px-2 py-3">{new Date(report.sentDate).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
