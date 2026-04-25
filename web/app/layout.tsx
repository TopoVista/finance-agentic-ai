import "./globals.css";

import { Providers } from "@/components/providers";

export const metadata = {
  title: "Finora",
  description: "FastAPI + Next.js AI finance workspace"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
