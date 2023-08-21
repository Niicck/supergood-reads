import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import MyMediaRow from '@/static/js/components/MyMediaRow.vue';
import MediaList from '@/static/js/views/MediaList/MediaList.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'my-media-row': MyMediaRow,
    'media-list': MediaList,
  },
});

const app = createApp(RootComponent);
app.mount('#my-media-app');

export {};
