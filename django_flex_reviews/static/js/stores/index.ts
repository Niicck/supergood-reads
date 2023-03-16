import { defineStore } from 'pinia';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';
import { ref, onMounted, watch } from 'vue';

interface State {
  selectedStrategyId: string;
  selectedMediaTypeContentType: string;
  selectedMediaTypeObjectId: string;
  createNewMediaTypeObject: boolean | undefined;
}

const useCreateReviewStore = defineStore('createReview', () => {
  const selectedStrategyId = ref('');
  const selectedMediaTypeContentType = ref('');
  const selectedMediaTypeObjectId = ref('');
  const createNewMediaTypeObject = ref(false);

  // Cache saved values when switching between MediaTypes
  const selectedMediaTypeObjectIdCache = ref<{ [key: string]: string }>({});

  // Save and retrieve ObjectId values to cache if we switch between ContentTypes
  watch(selectedMediaTypeContentType, (current, old) => {
    if (current !== old) {
      const cache = selectedMediaTypeObjectIdCache.value;

      // Save ObjectId into cache for the old active ContentType
      if (selectedMediaTypeObjectId.value) {
        cache[old] = selectedMediaTypeObjectId.value;
      }

      // If there's an existing ObjectId in the cache for the new ContentType, then
      // apply it. Otherwise, reset it.
      if (cache[current]) {
        selectedMediaTypeObjectId.value = cache[current];
      } else {
        selectedMediaTypeObjectId.value = '';
      }
    }
  });

  onMounted(() => {
    selectedStrategyId.value = parseJsonScriptFilter(
      'initialSelectedStrategyId',
    ) as string;
    selectedMediaTypeContentType.value = parseJsonScriptFilter(
      'initialSelectedMediaTypeContentType',
    ) as string;
    selectedMediaTypeObjectId.value = parseJsonScriptFilter(
      'initialSelectedMediaTypeObjectId',
    ) as string;
    createNewMediaTypeObject.value = parseJsonScriptFilter(
      'initialCreateNewMediaTypeObject',
    ) as boolean;
  });

  return {
    selectedStrategyId,
    selectedMediaTypeContentType,
    selectedMediaTypeObjectId,
    createNewMediaTypeObject,
  };
});

export { useCreateReviewStore };
export type { State };
