/* eslint-disable @typescript-eslint/no-var-requires */
import { defineConfig, loadEnv } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';

const postcssConfig = {
  plugins: [
    require('postcss-import')(),
    require('postcss-simple-vars')(),
    require('tailwindcss/nesting')(),
    require('tailwindcss')(),
    require('autoprefixer')(),
  ],
};

export default defineConfig((mode) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve('./django_flex_reviews'),
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
    root: resolve('./django_flex_reviews/static'),
    base: '/static/',
    css: {
      postcss: postcssConfig,
    },
    server: {
      port: env.DJANGO_VITE_DEV_SERVER_PORT,
    },
    build: {
      manifest: true,
      emptyOutDir: true,
      target: 'es2015',
      outDir: resolve(env.DJANGO_VITE_ASSETS_PATH),
      rollupOptions: {
        input: {
          autocomplete: resolve('./django_flex_reviews/static/js/apps/autocomplete.ts'),
          createReview: resolve('./django_flex_reviews/static/js/apps/createReview.ts'),
          tailwind: resolve('./django_flex_reviews/static/css/tailwind.css.js'),
          css: resolve('./django_flex_reviews/static/css/main.css.js'),
        },
        output: {
          chunkFileNames: undefined,
        },
      },
    },
  };
});
