import { useCreateReviewStore } from '@/static/js/stores';

/**
 * Define window.store type.
 */
declare global {
  interface Window {
    store: InstanceType<typeof useCreateReviewStore>;
  }
}
