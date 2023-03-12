import { defineStore } from 'pinia';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';

interface State {
  selectedStrategyId: string;
  selectedMediaTypeContentType: string;
  selectedMediaTypeObjectId: string;
}

const useCreateReviewStore = defineStore('createReview', {
  state: (): State => ({
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
    set(key: keyof State, value: string) {
      this[key] = value;
    },
  },
});

export { useCreateReviewStore };
export type { State };
