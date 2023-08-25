<template>
  <button
    class="rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
    @click="emit('click')"
  >
    {{ props.title }}
  </button>
</template>

<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['click']);
</script>
