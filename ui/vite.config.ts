import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/noxus/",
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8080",
      "/assets": "http://localhost:8080",
      "/files": "http://localhost:8080",
      "/socket.io": { target: "ws://localhost:8080", ws: true },
    },
  },
});
