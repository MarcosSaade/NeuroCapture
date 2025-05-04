import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, 'renderer'),

  base: './',

  plugins: [
    react(),
  ],

  build: {
    outDir: path.resolve(__dirname, 'renderer', 'dist'),
    emptyOutDir: true,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'renderer', 'src'),
    },
  },

  server: {
    port: 5173,
    strictPort: true,
  },
});
