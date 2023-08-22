import { defineStore } from 'pinia';
import { parseJsonScript } from '@/js/utils/parseJsonScript';
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

interface InitialData {
  selectedStrategyId: string;
  selectedMediaTypeContentType: string;
  selectedMediaTypeObjectId: string;
  createNewMediaTypeObject: CreateNewMediaOption;
}

enum CreateNewMediaOption {
  SELECT_EXISTING = 'SELECT_EXISTING',
  CREATE_NEW = 'CREATE_NEW',
}

const useReviewFormStore = defineStore('reviewForm', (): State => {
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
    /* Load initial data from django data loaded into "json_script".*/
    const initialData = parseJsonScript('initialDataForVueStore') as InitialData;

    selectedStrategyId.value = initialData.selectedStrategyId;
    selectedMediaTypeContentType.value = initialData.selectedMediaTypeContentType;
    selectedMediaTypeObjectId.value = initialData.selectedMediaTypeObjectId;
    createNewMediaTypeObject.value = initialData.createNewMediaTypeObject;
  });

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

export { useReviewFormStore };
export type { State };
