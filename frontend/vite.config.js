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
        login: resolve(__dirname, 'login.html'),
        trainer: resolve(__dirname, 'trainer.html'),
        client: resolve(__dirname, 'client.html'),
      },
    },
  },
  server: {
    port: 3000,
    open: '/home.html',
  },
});
