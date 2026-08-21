/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Syne', 'sans-serif'],
      },
      colors: {
        primary: '#0f172a',
        secondary: '#1e293b',
        accentGold: '#f59e0b',
        accentBlue: '#3b82f6',
        accentEmerald: '#10b981',
        // "brand" is used throughout the app — mapped to the gold accent scale
        brand: { 50: '#fffbeb', 100: '#fef3c7', 200: '#fde68a', 300: '#fcd34d', 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309' },
      },
      backgroundImage: {
        campus: "url('/vit-bg.jpg')",
      },
    },
  },
  plugins: [],
}
