import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
        '/api': {
            // 8000 常被 ASUS Gear Link 等 HTTP.sys 服务占用，默认改用 8001
            target: 'http://127.0.0.1:8001',
            changeOrigin: true,
        }
    },
  },
});
