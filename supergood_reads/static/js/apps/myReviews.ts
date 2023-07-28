import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import MyReviewsRow from '@/static/js/components/MyReviewsRow.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'my-reviews-row': MyReviewsRow,
  },
});

const app = createApp(RootComponent);
app.mount('#my-reviews-app');

export {};
