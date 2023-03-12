import { defineStore } from 'pinia';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';

const useCreateReviewStore = defineStore('createReview', {
  state: () => ({
    selectedStrategyId: '',
    selectedMediaTypeContentType: '',
    selectedMediaTypeObjectId: '',
  }),
  actions: {
    initiate() {
      this.selectedStrategyId = parseJsonScriptFilter(
        'initialSelectedStrategyId',
      ) as string;
      this.selectedMediaTypeContentType = parseJsonScriptFilter(
        'initialSelectedMediaTypeContentType',
      ) as string;
      this.selectedMediaTypeObjectId = parseJsonScriptFilter(
        'initialSelectedMediaTypeObjectId',
      ) as string;
    },
    set(key: string, value: string) {
      if (key === 'selectedMediaTypeObjectId') {
        this.selectedMediaTypeObjectId = value;
      }
    },
  },
});

export { useCreateReviewStore };
