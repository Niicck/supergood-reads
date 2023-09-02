import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import { createPinia, storeToRefs } from 'pinia';
import RadioCards from '@/js/components/forms/fields/RadioCards.vue';
import { useReviewFormStore } from '@/js/stores/reviewForm';
import ComboboxAutocomplete from '@/js/components/forms/fields/ComboboxAutocomplete.vue';
import DeleteModal from '@/js/components/DeleteModal.vue';
import FieldWrapper from '@/js/components/forms/layout/FieldWrapper.vue';
import DatePicker from '@/js/components/forms/fields/DatePicker.vue';

const pinia = createPinia();

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'radio-cards': RadioCards,
    'autocomplete': ComboboxAutocomplete,
    'delete-modal': DeleteModal,
    'field-wrapper': FieldWrapper,
    'date-picker': DatePicker,
  },
  setup() {
    const store = useReviewFormStore();

    const openDeleteReviewModal = () => {
      store.setShowDeleteReviewModal(true);
    };
    const closeDeleteReviewModal = () => {
      store.setShowDeleteReviewModal(false);
    };

    return { ...storeToRefs(store), openDeleteReviewModal, closeDeleteReviewModal };
  },
});

const app = createApp(RootComponent);
app.use(pinia);
app.mount('#review-form-vue-app');

export {};
