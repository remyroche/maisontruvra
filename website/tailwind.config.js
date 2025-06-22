/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./js/**/*.{vue,js,ts,jsx,tsx}", // Scans files in the js folder
    "./vue/**/*.{vue,js,ts,jsx,tsx}", // Add this to scan files in the vue folder
  ],
  theme: {
    extend: {
      colors: {
        'dark-gray': '#374151',
        'cream': '#FDFBF6',
        'dark-brown': '#433830',
        'truffle-burgundy': '#5C2C35',
        'gold': '#D4AF37',
        'light-gray': '#F3F4F6',
      },
      fontFamily: {
        sans: ['Raleway', 'sans-serif'],
        serif: ['Teko', 'serif'],
      }
    },
  },
  plugins: [],
}