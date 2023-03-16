import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import { createPinia } from 'pinia';
import RadioCards from '@/static/js/components/RadioCards.vue';
import { useCreateReviewStore } from '@/static/js/stores';
import ComboboxAutocomplete from '@/static/js/components/ComboboxAutocomplete.vue';

const pinia = createPinia();

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'radio-cards': RadioCards,
    'autocomplete': ComboboxAutocomplete,
  },
  setup() {
    const store = useCreateReviewStore();
    window.store = store;
    return { store };
  },
});

const app = createApp(RootComponent);
app.use(pinia);
app.mount('#review-form-vue-app');

export {};
