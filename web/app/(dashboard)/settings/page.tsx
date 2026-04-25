import { serverApiFetch } from "@/lib/api";

export default async function SettingsPage() {
  const response = await serverApiFetch<any>("/user/current-user");
  const user = response.user;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold">Settings</h2>
        <p className="mt-1 text-sm text-muted">Current account profile coming from the new FastAPI backend.</p>
      </div>
      <section className="rounded-md border border-border bg-panel p-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <div className="text-sm text-muted">Name</div>
            <div className="mt-2 text-lg font-semibold">{user.name}</div>
          </div>
          <div>
            <div className="text-sm text-muted">Email</div>
            <div className="mt-2 text-lg font-semibold">{user.email}</div>
          </div>
        </div>
      </section>
    </div>
  );
}
