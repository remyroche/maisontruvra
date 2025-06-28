import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()], // <-- A comma was likely missing here in your original file
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
    port: 5173, // Explicitly set the port
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: '../backend/static/dist',
    manifest: true,
    rollupOptions: {
      input: {
        app: path.resolve(__dirname, 'src/main.js'), // Use a single entry point for the entire SPA
      },
    },
  },
});