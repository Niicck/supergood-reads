import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import HomeFunDropdown from '@/js/components/HomeFunDropdown.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'home-fun-dropdown': HomeFunDropdown,
  },
});

const app = createApp(RootComponent);
app.mount('#home-app');

export {};
