import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent, ref } from 'vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {},
  setup() {
    const menuOpen = ref(false);

    const toggleMenuOpen = () => {
      menuOpen.value = !menuOpen.value;
    };

    return { menuOpen, toggleMenuOpen };
  },
});

const app = createApp(RootComponent);
app.mount('#new-nav-bar-vue-app');

export {};
