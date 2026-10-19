/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          dark: '#000000',
          card: '#0A0A0A',
          surface: '#121212',
          border: '#222222',
        },
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
        },
        status: {
          critical: '#EF4444',
          high: '#F97316',
          medium: '#F59E0B',
          low: '#3B82F6',
          info: '#71717A',
          success: '#10B981',
        }
      }
    },
  },
  plugins: [],
}
