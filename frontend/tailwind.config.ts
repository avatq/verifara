import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#0A0E17",
          900: "#0F1420",
          800: "#161C2C",
          700: "#212940",
        },
        accent: {
          violet: "#7C5CFF",
          blue: "#4F8CFF",
        },
        status: {
          good: "#22C55E",
          minor: "#F59E0B",
          low: "#38BDF8",
          conflict: "#EF4444",
          na: "#64748B",
        },
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
      },
    },
  },
  plugins: [],
};
export default config;
