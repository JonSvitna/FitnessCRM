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
        messages: resolve(__dirname, 'messages.html'),
        sms: resolve(__dirname, 'sms.html'),
        campaigns: resolve(__dirname, 'campaigns.html'),
        automation: resolve(__dirname, 'automation.html'),
        analytics: resolve(__dirname, 'analytics.html'),
      },
    },
  },
  server: {
    port: 3000,
    open: '/home.html',
  },
});
