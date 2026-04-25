"use client";

import { FormEvent, useState } from "react";

export function FinanceChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setAnswer("");

    try {
      const response = await fetch("/api/proxy/rag/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ question })
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Chat request failed");
      }

      const result = await response.json();
      setAnswer(result.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to answer that question right now.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-md border border-border bg-panel p-4">
      <div className="mb-3">
        <h3 className="text-lg font-semibold">Finance chat</h3>
        <p className="text-sm text-muted">Ask about spending patterns, category trends, or balance behavior.</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          className="min-h-24 w-full rounded-md border border-border px-3 py-2 outline-none focus:border-accent"
          placeholder="How much did I spend on groceries in the last month?"
        />
        <button type="submit" disabled={loading || !question.trim()} className="rounded-md bg-accent px-4 py-2 text-white disabled:opacity-60">
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>
      {error ? <p className="mt-3 text-sm text-danger">{error}</p> : null}
      {answer ? <div className="mt-4 rounded-md bg-accentSoft p-3 text-sm leading-6">{answer}</div> : null}
    </section>
  );
}
