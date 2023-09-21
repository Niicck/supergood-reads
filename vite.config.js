/* eslint-disable @typescript-eslint/no-var-requires */
import { defineConfig, loadEnv } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';

const INPUT_DIR = './supergood_reads/assets';
const OUTPUT_DIR = './supergood_reads/assets/dist';

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
        '@': resolve(INPUT_DIR),
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
    root: resolve(INPUT_DIR),
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
      outDir: resolve(OUTPUT_DIR),
      rollupOptions: {
        input: {
          reviewForm: resolve(`${INPUT_DIR}/js/apps/reviewForm.ts`),
          mediaForm: resolve(`${INPUT_DIR}/js/apps/mediaForm.ts`),
          messages: resolve(`${INPUT_DIR}/js/apps/messages.ts`),
          navBar: resolve(`${INPUT_DIR}/js/apps/navBar.ts`),
          library: resolve(`${INPUT_DIR}/js/apps/library.ts`),
          reviewList: resolve(`${INPUT_DIR}/js/apps/reviewList.ts`),
          userSettings: resolve(`${INPUT_DIR}/js/apps/userSettings.ts`),
          home: resolve(`${INPUT_DIR}/js/apps/home.ts`),
          css: resolve(`${INPUT_DIR}/css/main.css.js`),
        },
        output: {
          chunkFileNames: undefined,
        },
      },
    },
  };
});
