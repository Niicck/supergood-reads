import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent, ref } from 'vue';
import type { Ref } from 'vue';
import RadioCards from '@/js/components/forms/fields/RadioCards.vue';

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'radio-cards': RadioCards,
  },
  setup() {
    const selectedMediaTypeContentType: Ref<string> = ref('');

    return { selectedMediaTypeContentType };
  },
});

const app = createApp(RootComponent);
app.mount('#media-form-vue-app');

export {};
