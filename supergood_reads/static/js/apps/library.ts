import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import MyMediaRow from '@/js/components/MyMediaRow.vue';
import Library from '@/js/views/Library/Library.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'my-media-row': MyMediaRow,
    'library': Library,
  },
});

const app = createApp(RootComponent);
app.mount('#library-app');

export {};
