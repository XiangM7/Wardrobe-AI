import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "var(--canvas)",
        paper: "var(--paper)",
        ink: "var(--ink)",
        muted: "var(--muted)",
        accent: "var(--accent)",
        accentDeep: "var(--accent-deep)",
        mint: "var(--mint)",
        sand: "var(--sand)",
        line: "var(--line)",
      },
      boxShadow: {
        soft: "0 22px 40px rgba(44, 37, 30, 0.10)",
      },
      backgroundImage: {
        halo: "radial-gradient(circle at top right, rgba(211, 123, 74, 0.20), transparent 38%), radial-gradient(circle at bottom left, rgba(48, 93, 83, 0.18), transparent 35%)",
      },
      fontFamily: {
        display: ['"Iowan Old Style"', '"Palatino Linotype"', '"Book Antiqua"', "Georgia", "serif"],
        body: ['"Avenir Next"', "Avenir", '"Segoe UI"', "Helvetica Neue", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
