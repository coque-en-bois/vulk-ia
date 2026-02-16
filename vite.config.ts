import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");

  if (!env.VITE_BACKEND_API) {
    throw new Error("VITE_BACKEND_API environment variable is not set");
  }

  return {
    plugins: [react()],
    base: "./",
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: env.VITE_BACKEND_API,
          changeOrigin: true,
        },
      },
    },
  };
});
