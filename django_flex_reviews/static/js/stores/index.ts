import { defineStore } from 'pinia';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';

interface State {
  selectedStrategyId: string;
  selectedMediaTypeContentType: string;
  selectedMediaTypeObjectId: string;
  createNewMediaTypeObject: boolean | undefined;
}

const useCreateReviewStore = defineStore('createReview', {
  state: (): State => ({
    selectedStrategyId: '',
    selectedMediaTypeContentType: '',
    selectedMediaTypeObjectId: '',
    createNewMediaTypeObject: false,
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
      this.createNewMediaTypeObject = parseJsonScriptFilter(
        'initialCreateNewMediaTypeObject',
      ) as boolean;
    },
  },
});

export { useCreateReviewStore };
export type { State };
