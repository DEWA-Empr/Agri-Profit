/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f1f8f1',
          100: '#ddeedc',
          200: '#bddebb',
          300: '#8fc58c',
          400: '#5da45a',
          500: '#3d883b',
          600: '#2e6d2c',
          700: '#265725',
          800: '#214620',
          900: '#1c3a1b',
          950: '#0e200d',
        },
      }
    },
  },
  plugins: [],
}
