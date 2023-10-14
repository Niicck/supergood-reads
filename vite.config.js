/* eslint-disable @typescript-eslint/no-var-requires */
import { defineConfig, loadEnv } from 'vite';
import { resolve, join } from 'path';
import vue from '@vitejs/plugin-vue';

const INPUT_DIR = './supergood_reads/vite_assets';
const OUTPUT_DIR = './supergood_reads/vite_assets_dist/supergood_reads/vite';

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
      host: env.DJANGO_VITE_DEV_SERVER_HOST,
      port: env.DJANGO_VITE_DEV_SERVER_PORT,
    },
    build: {
      manifest: true,
      emptyOutDir: true,
      target: 'es2015',
      outDir: resolve(OUTPUT_DIR),
      rollupOptions: {
        input: {
          reviewForm: join(INPUT_DIR, '/js/apps/reviewForm.ts'),
          mediaForm: join(INPUT_DIR, '/js/apps/mediaForm.ts'),
          messages: join(INPUT_DIR, '/js/apps/messages.ts'),
          navBar: join(INPUT_DIR, '/js/apps/navBar.ts'),
          library: join(INPUT_DIR, '/js/apps/library.ts'),
          reviewList: join(INPUT_DIR, '/js/apps/reviewList.ts'),
          userSettings: join(INPUT_DIR, '/js/apps/userSettings.ts'),
          home: join(INPUT_DIR, '/js/apps/home.ts'),
          css: join(INPUT_DIR, '/css/main.css.js'),
        },
        output: {
          chunkFileNames: undefined,
        },
      },
    },
  };
});
