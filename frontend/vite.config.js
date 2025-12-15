import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: '.',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'home.html'),
        app: resolve(__dirname, 'index.html'),
      },
    },
  },
  server: {
    port: 3000,
    open: '/home.html',
  },
});
