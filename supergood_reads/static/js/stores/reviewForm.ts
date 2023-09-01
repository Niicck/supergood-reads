import { defineStore } from 'pinia';
import { parseJsonScript } from '@/js/utils/parseJsonScript';
import { ref, onMounted, watch, computed } from 'vue';
import type { Ref, ComputedRef } from 'vue';

interface State {
  selectedStrategyId: Ref<string>;
  selectedMediaItemContentType: Ref<number>;
  selectedMediaItemObjectId: Ref<string>;
  createNewMediaItemObject: Ref<CreateNewMediaOption>;
  shouldCreateNewMediaItemObject: ComputedRef<boolean>;
  showDeleteReviewModal: Ref<boolean>;
  autocompleteUrl: Ref<string>;
  setShowDeleteReviewModal: (value: boolean) => void;
}

interface InitialData {
  selectedStrategyId: string;
  selectedMediaItemContentType: string;
  selectedMediaItemObjectId: string;
  createNewMediaItemObject: CreateNewMediaOption;
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
  const createNewMediaItemObject = ref(CreateNewMediaOption.SELECT_EXISTING);
  const selectedStrategyId = ref();
  const selectedMediaItemContentType = ref();
  const selectedMediaItemObjectId = ref();
  // Cache the selectedMediaItemObjectId for each MediaItem.
  const selectedMediaItemObjectIdCache = ref<{ [key: string]: string }>({});
  const autocompleteUrlBase = ref('');
  const autocompleteUrl = computed((): string => {
    if (autocompleteUrlBase.value && selectedMediaItemContentType.value) {
      let url = autocompleteUrlBase.value;
      url += `?content_type_id=${selectedMediaItemContentType.value}`;
      return url;
    }
    return '';
  });

  onMounted(() => {
    /* Load initial data from django data loaded into "json_script".*/
    const initialData = parseJsonScript('initialDataForVueStore') as InitialData;
    createNewMediaItemObject.value = initialData.createNewMediaItemObject;
    selectedStrategyId.value = initialData.selectedStrategyId;
    selectedMediaItemContentType.value = initialData.selectedMediaItemContentType;
    selectedMediaItemObjectId.value = initialData.selectedMediaItemObjectId;
    autocompleteUrlBase.value = initialData.autocompleteUrlBase;
  });

  /**
   * Handle Delete Modal
   */
  const showDeleteReviewModal = ref(false);
  const setShowDeleteReviewModal = (value: boolean): void => {
    showDeleteReviewModal.value = value;
  };

  // Inform UI that we want to create a new MediaItem object instead of selecting an
  // existing one.
  const shouldCreateNewMediaItemObject = computed((): boolean => {
    return createNewMediaItemObject.value === CreateNewMediaOption.CREATE_NEW;
  });

  /**
   * Handle selectedMediaItemObjectId caching when switching between
   * selectedMediaItemContentTypes.
   *
   * Save and retrieve ObjectId values from cache if we switch between ContentTypes.
   */
  watch(
    selectedMediaItemContentType,
    (newValue, oldValue) => {
      const cache = selectedMediaItemObjectIdCache.value;

      // Save ObjectId into cache for the old active ContentType
      if (selectedMediaItemObjectId.value) {
        cache[oldValue] = selectedMediaItemObjectId.value;
      }

      // If there's an existing ObjectId in the cache for the new ContentType, then
      // apply it. Otherwise, reset it.
      if (cache[newValue]) {
        selectedMediaItemObjectId.value = cache[newValue];
      } else {
        selectedMediaItemObjectId.value = '';
      }
    },
    { flush: 'sync' },
  );

  return {
    selectedStrategyId,
    selectedMediaItemContentType,
    selectedMediaItemObjectId,
    createNewMediaItemObject,
    shouldCreateNewMediaItemObject,
    showDeleteReviewModal,
    autocompleteUrl,
    setShowDeleteReviewModal,
  };
});

export { useReviewFormStore };
export type { State };
