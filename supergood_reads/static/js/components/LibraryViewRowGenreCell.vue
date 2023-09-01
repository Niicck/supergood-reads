<template>
  <div class="space-y-1">
    <button
      v-for="(genre, idx) in props.genres"
      :key="idx"
      type="button"
      class="rounded-full mx-0.5 bg-white px-2.5 py-1 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
      :class="{ 'selected-genre': props.selectedGenres.includes(genre) }"
      @click="emit('toggle-checked-genre', genre)"
    >
      {{ genre }}
    </button>
  </div>
</template>

<script lang="ts" setup>
import { PropType } from 'vue';

const props = defineProps({
  genres: { type: Array as PropType<string[]>, default: () => [] },
  selectedGenres: { type: Array as PropType<string[]>, required: true },
});

const emit = defineEmits(['toggle-checked-genre']);
</script>

<style scoped>
.selected-genre {
  @apply bg-indigo-600 text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600;
}
</style>
