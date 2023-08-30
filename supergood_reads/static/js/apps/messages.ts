import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import { createPinia, storeToRefs } from 'pinia';
import { useMessagesStore } from '@/js/stores/messages';
import SimpleNotifcation from '@/js/components/SimpleNotification.vue';

const pinia = createPinia();

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'simple-notification': SimpleNotifcation,
  },
  setup() {
    const store = useMessagesStore();
    return { ...storeToRefs(store) };
  },
});

const app = createApp(RootComponent);
app.use(pinia);
app.mount('#messages-vue-app');

export {};
