import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import RadioCards from '@/static/js/components/RadioCards.vue';
import { parseJsonScriptFilter } from '../utils/parseJsonScriptFilter';

const ReviewFormRootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'radio-cards': RadioCards,
  },
  data() {
    return {
      selectedStrategyId: parseJsonScriptFilter('initialSelectedStrategyId'),
      selectedMediaTypeContentType: parseJsonScriptFilter(
        'initialSelectedMediaTypeContentType',
      ),
      selectedMediaTypeObjectId: parseJsonScriptFilter(
        'initialSelectedMediaTypeObjectId',
      ),
    };
  },
});

const reviewFormApp = createApp(ReviewFormRootComponent);

reviewFormApp.mount('#review-form-vue-app');

export {};
