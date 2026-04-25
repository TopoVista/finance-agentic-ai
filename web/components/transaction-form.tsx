"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export function TransactionForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    const formData = new FormData(event.currentTarget);
    const payload = {
      title: formData.get("title"),
      description: formData.get("description") || null,
      type: formData.get("type"),
      amount: Number(formData.get("amount")),
      category: formData.get("category"),
      date: new Date(String(formData.get("date"))).toISOString(),
      isRecurring: formData.get("isRecurring") === "on",
      recurringInterval: formData.get("recurringInterval") || null,
      receiptUrl: null,
      paymentMethod: formData.get("paymentMethod")
    };

    const response = await fetch("/api/proxy/transaction/create", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const text = await response.text();
      setError(text || "Unable to create transaction");
      setLoading(false);
      return;
    }

    event.currentTarget.reset();
    router.refresh();
    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3 rounded-md border border-border bg-panel p-4 md:grid-cols-2 xl:grid-cols-4">
      <input name="title" placeholder="Title" required className="rounded-md border border-border px-3 py-2" />
      <input name="category" placeholder="Category" required className="rounded-md border border-border px-3 py-2" />
      <input name="amount" type="number" min="1" step="0.01" placeholder="Amount" required className="rounded-md border border-border px-3 py-2" />
      <input name="date" type="datetime-local" required className="rounded-md border border-border px-3 py-2" />
      <select name="type" defaultValue="EXPENSE" className="rounded-md border border-border px-3 py-2">
        <option value="EXPENSE">Expense</option>
        <option value="INCOME">Income</option>
      </select>
      <select name="paymentMethod" defaultValue="CASH" className="rounded-md border border-border px-3 py-2">
        <option value="CASH">Cash</option>
        <option value="CARD">Card</option>
        <option value="BANK_TRANSFER">Bank transfer</option>
        <option value="MOBILE_PAYMENT">Mobile payment</option>
        <option value="AUTO_DEBIT">Auto debit</option>
        <option value="OTHER">Other</option>
      </select>
      <select name="recurringInterval" defaultValue="" className="rounded-md border border-border px-3 py-2">
        <option value="">Not recurring</option>
        <option value="DAILY">Daily</option>
        <option value="WEEKLY">Weekly</option>
        <option value="MONTHLY">Monthly</option>
        <option value="YEARLY">Yearly</option>
      </select>
      <label className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm">
        <input name="isRecurring" type="checkbox" />
        <span>Recurring</span>
      </label>
      <textarea
        name="description"
        placeholder="Description"
        className="md:col-span-2 xl:col-span-4 min-h-24 rounded-md border border-border px-3 py-2"
      />
      {error ? <p className="md:col-span-2 xl:col-span-4 text-sm text-danger">{error}</p> : null}
      <div className="md:col-span-2 xl:col-span-4">
        <button type="submit" disabled={loading} className="rounded-md bg-accent px-4 py-2 text-white disabled:opacity-60">
          {loading ? "Saving..." : "Add transaction"}
        </button>
      </div>
    </form>
  );
}
