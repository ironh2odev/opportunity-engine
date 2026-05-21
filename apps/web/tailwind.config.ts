import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#090b10",
        panel: "#111522",
        accent: "#4ce2b1",
        signal: "#f6b72f",
      },
      boxShadow: {
        aura: "0 0 0 1px rgba(255,255,255,0.08), 0 20px 50px rgba(2, 6, 23, 0.45)",
      },
      backgroundImage: {
        "mesh-gradient":
          "radial-gradient(circle at 12% 10%, rgba(76,226,177,.2), transparent 35%), radial-gradient(circle at 88% 0%, rgba(246,183,47,.15), transparent 28%), linear-gradient(180deg, #0a0e16 0%, #080a0f 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
