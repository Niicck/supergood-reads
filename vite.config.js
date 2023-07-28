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
        '@': resolve('./supergood_review_site'),
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
    root: resolve('./supergood_review_site/static'),
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
          createReview: resolve(
            './supergood_review_site/static/js/apps/createReview.ts',
          ),
          messages: resolve('./supergood_review_site/static/js/apps/messages.ts'),
          navBar: resolve('./supergood_review_site/static/js/apps/navBar.ts'),
          myMedia: resolve('./supergood_review_site/static/js/apps/myMedia.ts'),
          reviewList: resolve('./supergood_review_site/static/js/apps/reviewList.ts'),
          tailwind: resolve('./supergood_review_site/static/css/tailwind.css.js'),
          css: resolve('./supergood_review_site/static/css/main.css.js'),
        },
        output: {
          chunkFileNames: undefined,
        },
      },
    },
  };
});
