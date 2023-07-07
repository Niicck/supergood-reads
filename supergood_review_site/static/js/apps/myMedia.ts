import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import MyMediaRow from '@/static/js/components/MyMediaRow.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'my-media-row': MyMediaRow,
  },
});

const app = createApp(RootComponent);
app.mount('#my-media-app');

export {};
