import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import SimpleNotifcation from '@/static/js/components/SimpleNotification.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'simple-notification': SimpleNotifcation,
  },
});

const app = createApp(RootComponent);
app.mount('#messages-vue-app');

export {};
