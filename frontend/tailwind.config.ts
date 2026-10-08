import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        soc: { bg: "#0a0e1a", card: "#111827", border: "#1e293b", accent: "#3b82f6", glow: "#60a5fa" },
      },
    },
  },
  plugins: [],
};
export default config;
