// Minimal Vite config for CDN-based Tailwind dev
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: __dirname,
  base: './',
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  build: {
    outDir: path.resolve(__dirname, 'dist'),
    emptyOutDir: true,
    assetsDir: '',
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: { allow: [__dirname] },
    hmr: { overlay: false }
  },
});
