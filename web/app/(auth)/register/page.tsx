import Link from "next/link";

import { AuthForm } from "@/components/auth-form";

export default function RegisterPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-4">
      <div className="w-full space-y-4">
        <AuthForm mode="register" />
        <p className="text-center text-sm text-muted">
          Already have an account? <Link href="/login" className="font-medium text-accent">Sign in</Link>
        </p>
      </div>
    </main>
  );
}
