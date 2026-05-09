import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        ui: ["Inter", "system-ui", "sans-serif"],
        data: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        "row-glow": "0 0 0 1px rgba(16,185,129,0.8), 0 0 14px rgba(16,185,129,0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
