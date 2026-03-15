import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  root: ".",
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: "index.html",
    },
  },
  server: {
    port: 5174,
    proxy: {
      "/api": "http://localhost:18790",
      "/ws": "http://localhost:18790",
    },
  },
});
