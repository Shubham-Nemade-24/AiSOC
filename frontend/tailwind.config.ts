import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"], mono: ["JetBrains Mono", "Menlo", "monospace"] },
      colors: {
        soc: { bg: "#050816", card: "rgba(15,23,42,0.6)", border: "rgba(56,78,126,0.25)" },
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "glow-pulse": "glowPulse 3s ease-in-out infinite",
        "slide-up": "slideUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards",
        "fade-in": "fadeIn 0.6s ease-out forwards",
      },
    },
  },
  plugins: [],
};
export default config;
