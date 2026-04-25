import Link from "next/link";
import { BarChart3, LayoutDashboard, ReceiptText, ScrollText, Settings } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: ReceiptText },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/reports", label: "Reports", icon: ScrollText },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-0 lg:grid-cols-[240px_1fr]">
        <aside className="border-b border-border bg-panel p-5 lg:border-b-0 lg:border-r">
          <div className="mb-8">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted">Finora</div>
            <h1 className="mt-2 text-2xl font-semibold">Finance workspace</h1>
          </div>
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-md border border-transparent px-3 py-2 text-sm text-foreground transition hover:border-border hover:bg-accentSoft"
                >
                  <Icon size={16} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </aside>
        <main className="p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
