import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent, ref } from 'vue';
import DeleteButton from '@/js/components/DeleteButton.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'delete-button': DeleteButton,
  },
  setup() {
    const showDangerZone = ref(false);
    return { showDangerZone };
  },
});

const app = createApp(RootComponent);
app.mount('#user-settings-app');

export {};
