import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
    open: false,
    host: true,
    proxy: {
      '/chat': 'http://127.0.0.1:10000',
      '/api': 'http://127.0.0.1:10000',
      '/public': 'http://127.0.0.1:10000',
      '/ping': 'http://127.0.0.1:10000',
      '/health': 'http://127.0.0.1:10000',
      '/upload': 'http://127.0.0.1:10000',
      '/documents': 'http://127.0.0.1:10000',
      '/provision': 'http://127.0.0.1:10000',
      '/amendment-coverage': 'http://127.0.0.1:10000',
      '/feedback': 'http://127.0.0.1:10000',
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
