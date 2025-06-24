import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import { glob } from 'glob';

// Find all HTML and JS entry points
const htmlEntryPoints = glob.sync('./website/**/*.html');
const jsEntryPoints = glob.sync('./website/js/pages/*.js');
const proJsEntryPoints = glob.sync('./website/pro/js/*.js');
const allEntryPoints = [...htmlEntryPoints, ...jsEntryPoints, ...proJsEntryPoints];

export default defineConfig({
  plugins: [vue()],
  root: 'website', // Set the project root to the 'website' directory
  build: {
    outDir: '../dist', // Output to a 'dist' directory at the project root
    emptyOutDir: true, // Clear the output directory on each build
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'website/index.html'),
        // Automatically include other HTML files as entry points
        ...Object.fromEntries(
          allEntryPoints.map(file => [
            // Generate a name for the entry point
            resolve(file).replace(resolve(__dirname, 'website') + '/', '').replace('.html', ''),
            file
          ])
        )
      },
    },
    manifest: true, // Generate a manifest.json file for backend integration
  },
  server: {
    // Set up a proxy for API requests to the Flask backend during development
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
});
