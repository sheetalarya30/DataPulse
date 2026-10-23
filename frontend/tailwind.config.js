/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#060913",
          900: "#0a0f1d",
          850: "#0f1629",
          800: "#152038",
          700: "#1e2c4f",
          600: "#2a3d6d",
          500: "#3d5694",
        },
        pulse: {
          cyan: "#00f0ff",
          blue: "#3b82f6",
          violet: "#8b5cf6",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
}
