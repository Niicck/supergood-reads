import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import NavBar from '@/static/js/components/NavBar.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'nav-bar': NavBar,
  },
});

const app = createApp(RootComponent);
app.mount('#nav-bar-vue-app');

export {};
