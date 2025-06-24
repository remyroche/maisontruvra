/** @type {import('tailwindcss').Config} */
module.exports = {
  // Rigorously scan all relevant files for Tailwind classes.
  // This is the most critical step for reducing CSS bundle size.
  content: [
    './website/**/*.html', // All static and Jinja2-generated HTML
    './website/**/*.vue',   // All Vue components
    './website/**/*.js',    // All JavaScript files (for dynamic classes)
    './backend/templates/**/*.html', // All backend Jinja2 templates
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
        signature: ['Dancing Script', 'cursive'],
      },
      colors: {
        'brand-dark-brown': '#3a322f',
        'brand-cream': '#f9f5f0',
        'brand-burgundy': '#800020',
        'brand-light-gray': '#e9e9e9',
        'brand-dark-gray': '#5a5a5a',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
