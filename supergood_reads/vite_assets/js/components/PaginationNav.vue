<template>
  <nav
    class="flex flex-col sm:flex-row items-center justify-between border-t border-gray-200 bg-white py-3"
    aria-label="Pagination"
  >
    <div class="order-last sm:order-first pt-3 sm:pt-0">
      <p class="text-sm text-gray-700">
        Showing
        <span class="font-medium">{{ props.startIndex }}</span>
        to
        <span class="font-medium">{{ props.endIndex }}</span>
        of
        <span class="font-medium">{{ props.count }}</span>
        results
      </p>
    </div>
    <div class="flex flex-1 justify-between sm:justify-end w-full">
      <template v-if="props.hasPrevious">
        <button
          class="relative inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:outline-offset-0"
          @click="emit('previous')"
        >
          Previous
        </button>
      </template>
      <template v-else>
        <div></div>
      </template>
      <template v-if="props.hasNext">
        <button
          class="relative ml-3 inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:outline-offset-0"
          @click="emit('next')"
        >
          Next
        </button>
      </template>
      <template v-else>
        <div></div>
      </template>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { PropType } from 'vue';

const props = defineProps({
  hasNext: { type: Boolean as PropType<boolean>, required: true },
  hasPrevious: { type: Boolean as PropType<boolean>, required: true },
  startIndex: { type: Number as PropType<number>, required: true },
  endIndex: { type: Number as PropType<number>, required: true },
  count: { type: Number as PropType<number>, required: true },
});

const emit = defineEmits(['previous', 'next']);
</script>
