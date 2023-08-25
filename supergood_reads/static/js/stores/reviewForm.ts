import { defineStore } from 'pinia';
import { parseJsonScript } from '@/js/utils/parseJsonScript';
import { ref, onMounted, watch, computed } from 'vue';
import type { Ref, ComputedRef } from 'vue';

interface State {
  selectedStrategyId: Ref<string>;
  selectedMediaTypeContentType: Ref<number>;
  selectedMediaTypeObjectId: Ref<string>;
  createNewMediaTypeObject: Ref<CreateNewMediaOption>;
  shouldCreateNewMediaTypeObject: ComputedRef<boolean>;
  showDeleteReviewModal: Ref<boolean>;
  autocompleteUrl: Ref<string>;
  setShowDeleteReviewModal: (value: boolean) => void;
}

interface InitialData {
  selectedStrategyId: string;
  selectedMediaTypeContentType: string;
  selectedMediaTypeObjectId: string;
  createNewMediaTypeObject: CreateNewMediaOption;
  autocompleteUrlBase: string;
}

enum CreateNewMediaOption {
  SELECT_EXISTING = 'SELECT_EXISTING',
  CREATE_NEW = 'CREATE_NEW',
}

const useReviewFormStore = defineStore('reviewForm', (): State => {
  /**
   * Handle initial values for django fields bound to v-models.
   */
  const createNewMediaTypeObject = ref(CreateNewMediaOption.SELECT_EXISTING);
  const selectedStrategyId = ref();
  const selectedMediaTypeContentType = ref();
  const selectedMediaTypeObjectId = ref();
  // Cache the selectedMediaTypeObjectId for each MediaType.
  const selectedMediaTypeObjectIdCache = ref<{ [key: string]: string }>({});
  const autocompleteUrlBase = ref('');
  const autocompleteUrl = computed((): string => {
    if (autocompleteUrlBase.value && selectedMediaTypeContentType.value) {
      let url = autocompleteUrlBase.value;
      url += `?content_type_id=${selectedMediaTypeContentType.value}`;
      return url;
    }
    return '';
  });

  onMounted(() => {
    /* Load initial data from django data loaded into "json_script".*/
    const initialData = parseJsonScript('initialDataForVueStore') as InitialData;
    createNewMediaTypeObject.value = initialData.createNewMediaTypeObject;
    selectedStrategyId.value = initialData.selectedStrategyId;
    selectedMediaTypeContentType.value = initialData.selectedMediaTypeContentType;
    selectedMediaTypeObjectId.value = initialData.selectedMediaTypeObjectId;
    autocompleteUrlBase.value = initialData.autocompleteUrlBase;
  });

  /**
   * Handle Delete Modal
   */
  const showDeleteReviewModal = ref(false);
  const setShowDeleteReviewModal = (value: boolean): void => {
    showDeleteReviewModal.value = value;
  };

  // Inform UI that we want to create a new MediaType object instead of selecting an
  // existing one.
  const shouldCreateNewMediaTypeObject = computed((): boolean => {
    return createNewMediaTypeObject.value === CreateNewMediaOption.CREATE_NEW;
  });

  /**
   * Handle selectedMediaTypeObjectId caching when switching between
   * selectedMediaTypeContentTypes.
   *
   * Save and retrieve ObjectId values from cache if we switch between ContentTypes.
   */
  watch(
    selectedMediaTypeContentType,
    (newValue, oldValue) => {
      const cache = selectedMediaTypeObjectIdCache.value;

      // Save ObjectId into cache for the old active ContentType
      if (selectedMediaTypeObjectId.value) {
        cache[oldValue] = selectedMediaTypeObjectId.value;
      }

      // If there's an existing ObjectId in the cache for the new ContentType, then
      // apply it. Otherwise, reset it.
      if (cache[newValue]) {
        selectedMediaTypeObjectId.value = cache[newValue];
      } else {
        selectedMediaTypeObjectId.value = '';
      }
    },
    { flush: 'sync' },
  );

  return {
    selectedStrategyId,
    selectedMediaTypeContentType,
    selectedMediaTypeObjectId,
    createNewMediaTypeObject,
    shouldCreateNewMediaTypeObject,
    showDeleteReviewModal,
    autocompleteUrl,
    setShowDeleteReviewModal,
  };
});

export { useReviewFormStore };
export type { State };
