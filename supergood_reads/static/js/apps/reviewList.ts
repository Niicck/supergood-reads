import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import ReviewListRowText from '@/js/components/ReviewListRowText.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'review-list-row-text': ReviewListRowText,
  },
});

const app = createApp(RootComponent);
app.mount('#review-list-vue-app');

export {};
