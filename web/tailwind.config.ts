import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#0f3460",
        teal: "#008080",
        slatebg: "#f5f7fa",
      },
    },
  },
  plugins: [],
};

export default config;
