import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import ReviewRowText from '@/static/js/components/ReviewRowText.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'review-row-text': ReviewRowText,
  },
});

const app = createApp(RootComponent);
app.mount('#review-list-vue-app');

export {};
