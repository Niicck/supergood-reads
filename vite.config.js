/* eslint-disable @typescript-eslint/no-var-requires */
import { defineConfig, loadEnv } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';

const STATIC_DIR = './supergood_reads/assets/src';

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
        '@': resolve(STATIC_DIR),
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
    root: resolve(STATIC_DIR),
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
      outDir: resolve('./supergood_reads/assets/dist/supergood_reads'),
      rollupOptions: {
        input: {
          reviewForm: resolve(`${STATIC_DIR}/js/apps/reviewForm.ts`),
          mediaForm: resolve(`${STATIC_DIR}/js/apps/mediaForm.ts`),
          messages: resolve(`${STATIC_DIR}/js/apps/messages.ts`),
          navBar: resolve(`${STATIC_DIR}/js/apps/navBar.ts`),
          library: resolve(`${STATIC_DIR}/js/apps/library.ts`),
          reviewList: resolve(`${STATIC_DIR}/js/apps/reviewList.ts`),
          userSettings: resolve(`${STATIC_DIR}/js/apps/userSettings.ts`),
          home: resolve(`${STATIC_DIR}/js/apps/home.ts`),
          css: resolve(`${STATIC_DIR}/css/main.css.js`),
        },
        output: {
          chunkFileNames: undefined,
        },
      },
    },
  };
});
