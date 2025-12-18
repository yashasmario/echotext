
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    // In Vite 6, use 'true' (boolean) to allow all hostnames
    allowedHosts: true,
    host: true,
    port: 5173,
    cors: true,
    // Helping HMR (Hot Module Replacement) work better over a tunnel
    hmr: {
      clientPort: 443,
    },
  },
});
