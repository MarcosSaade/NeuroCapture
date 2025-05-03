import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: './renderer',
  plugins: [react()],
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './renderer/src'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
  },
});