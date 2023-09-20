import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent, ref } from 'vue';
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'headless-menu': Menu,
    'headless-menu-button': MenuButton,
    'headless-menu-items': MenuItems,
    'headless-menu-item': MenuItem,
  },
  setup() {
    const menuOpen = ref(false);

    const toggleMenuOpen = () => {
      menuOpen.value = !menuOpen.value;
    };

    return { menuOpen, toggleMenuOpen };
  },
});

const app = createApp(RootComponent);
app.mount('#nav-bar-vue-app');

export {};
