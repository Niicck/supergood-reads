import { defineConfig, loadEnv } from "vite";
import { resolve } from "path";

export default defineConfig((mode) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    resolve: {
      alias: {
        "@": resolve("./django_flex_reviews"),
      },
    },
    root: resolve("./django_flex_reviews/static"),
    base: "/static/",
    server: {
      port: env.DJANGO_VITE_DEV_SERVER_PORT,
    },
    build: {
      manifest: true,
      emptyOutDir: true,
      target: "es2015",
      outDir: resolve(env.DJANGO_VITE_ASSETS_PATH),
      rollupOptions: {
        input: {
          form: resolve("./django_flex_reviews/static/js/form.ts"),
          css: resolve("./django_flex_reviews/static/css/main.css.js"),
        },
        output: {
          chunkFileNames: undefined,
        },
      },
    },
  };
});
