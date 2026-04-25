"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

type Mode = "login" | "register";

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const payload =
      mode === "login"
        ? {
            email: formData.get("email"),
            password: formData.get("password")
          }
        : {
            name: formData.get("name"),
            email: formData.get("email"),
            password: formData.get("password")
          };

    const response = await fetch(`/api/proxy/auth/${mode === "login" ? "login" : "register"}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include"
    });

    if (!response.ok) {
      const text = await response.text();
      setError(text || "Authentication failed");
      setLoading(false);
      return;
    }

    router.push("/dashboard");
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-border bg-panel p-6 shadow-sm">
      <div>
        <h2 className="text-2xl font-semibold">{mode === "login" ? "Welcome back" : "Create your account"}</h2>
        <p className="mt-1 text-sm text-muted">
          {mode === "login" ? "Sign in to your finance workspace." : "Start tracking, analyzing, and reporting from one place."}
        </p>
      </div>
      {mode === "register" ? (
        <label className="block">
          <span className="mb-1 block text-sm font-medium">Name</span>
          <input name="name" required className="w-full rounded-md border border-border px-3 py-2 outline-none focus:border-accent" />
        </label>
      ) : null}
      <label className="block">
        <span className="mb-1 block text-sm font-medium">Email</span>
        <input
          name="email"
          type="email"
          required
          className="w-full rounded-md border border-border px-3 py-2 outline-none focus:border-accent"
        />
      </label>
      <label className="block">
        <span className="mb-1 block text-sm font-medium">Password</span>
        <input
          name="password"
          type="password"
          required
          minLength={4}
          className="w-full rounded-md border border-border px-3 py-2 outline-none focus:border-accent"
        />
      </label>
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-accent px-4 py-2 font-medium text-white disabled:opacity-60"
      >
        {loading ? "Working..." : mode === "login" ? "Sign in" : "Create account"}
      </button>
    </form>
  );
}
