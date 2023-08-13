import { useReviewFormStore } from '@/static/js/stores/reviewForm';

/**
 * Define window.store type.
 */
declare global {
  interface Window {
    store: InstanceType<typeof useReviewFormStore>;
  }
}
