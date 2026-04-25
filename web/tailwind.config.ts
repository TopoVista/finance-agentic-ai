import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#f7faf8",
        panel: "#ffffff",
        foreground: "#111827",
        muted: "#6b7280",
        border: "#d1d5db",
        accent: "#0f766e",
        accentSoft: "#ccfbf1",
        danger: "#dc2626"
      }
    }
  },
  plugins: []
};

export default config;
