import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import MyMediaRow from '@/js/components/MyMediaRow.vue';
import LibraryView from '@/js/views/Library/LibraryView.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'library-view': LibraryView,
  },
});

const app = createApp(RootComponent);
app.mount('#library-app');

export {};
