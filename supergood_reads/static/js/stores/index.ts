import { defineStore } from 'pinia';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';
import { ref, onMounted, watch, computed } from 'vue';
import type { Ref, ComputedRef } from 'vue';

interface State {
  selectedStrategyId: Ref<string>;
  selectedMediaTypeContentType: Ref<string>;
  selectedMediaTypeObjectId: Ref<string>;
  createNewMediaTypeObject: Ref<CreateNewMediaOption>;
  shouldCreateNewMediaTypeObject: ComputedRef<boolean>;
  showDeleteReviewModal: Ref<boolean>;
  setShowDeleteReviewModal: (value: boolean) => void;
}

enum CreateNewMediaOption {
  SELECT_EXISTING = 'SELECT_EXISTING',
  CREATE_NEW = 'CREATE_NEW',
}

const useCreateReviewStore = defineStore('createReview', (): State => {
  const selectedStrategyId = ref('');
  const selectedMediaTypeContentType = ref('');
  const selectedMediaTypeObjectId = ref('');
  const createNewMediaTypeObject = ref(CreateNewMediaOption.SELECT_EXISTING);
  const showDeleteReviewModal = ref(false);

  // Cache saved values when switching between MediaTypes
  const selectedMediaTypeObjectIdCache = ref<{ [key: string]: string }>({});

  // Inform UI that we want to create a new MediaType object instead of selecting an
  // existing one.
  const shouldCreateNewMediaTypeObject = computed((): boolean => {
    return createNewMediaTypeObject.value === CreateNewMediaOption.CREATE_NEW;
  });

  // Turn showDeleteReviewModal on or off.
  const setShowDeleteReviewModal = (value: boolean): void => {
    showDeleteReviewModal.value = value;
  };

  // Save and retrieve ObjectId values from cache if we switch between ContentTypes.
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
    ) as CreateNewMediaOption;
  });

  console.log(`##### bottom of store::: ${showDeleteReviewModal.value}`);
  return {
    selectedStrategyId,
    selectedMediaTypeContentType,
    selectedMediaTypeObjectId,
    createNewMediaTypeObject,
    shouldCreateNewMediaTypeObject,
    showDeleteReviewModal,
    setShowDeleteReviewModal,
  };
});

export { useCreateReviewStore };
export type { State };
