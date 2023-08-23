<template>
  <tr class="border-none review-row-vue-app">
    <td class="pb-4" colspan="2" aria-label="Review Text">
      <div class="grid">
        <p ref="textContainer" :class="{ truncate: !expanded }">{{ text }}</p>
        <span v-if="hasMore">
          <button
            type="button"
            class="rounded bg-white px-2 py-1 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            @click="expanded = !expanded"
          >
            {{ expanded ? 'Show less' : 'Show more' }}
          </button>
        </span>
      </div>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import type { Ref } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
});

const expanded = ref(false);
const textContainer: Ref<HTMLElement | null> = ref(null);

const hasMore = computed(() => {
  const el = textContainer.value;
  if (el && el.scrollWidth > el.clientWidth) {
    return true;
  }
  return false;
});
</script>
