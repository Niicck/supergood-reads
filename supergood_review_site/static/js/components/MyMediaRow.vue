<template>
  <tr>
    <td
      class="w-full max-w-0 py-4 pr-3 text-sm font-medium text-gray-900 sm:w-auto sm:max-w-none sm:pl-0"
    >
      <span v-show="editMode"> We're in edit Mode!!!</span>
      {{ title }}
      <dl class="font-normal lg:hidden">
        <dt class="sr-only">Author</dt>
        <dd class="mt-1 truncate text-gray-700">{{ author }}</dd>
        <dt class="sr-only sm:hidden">Year</dt>
        <dd class="mt-1 truncate text-gray-500 sm:hidden">{{ year }}</dd>
      </dl>
    </td>
    <td class="hidden px-3 py-4 text-sm text-gray-500 lg:table-cell">{{ author }}</td>
    <td class="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">{{ year }}</td>
    <td class="px-3 py-4 text-sm text-gray-500 sm:table-cell">{{ mediaType }}</td>
    <td class="py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
      <button
        type="button"
        class="text-indigo-600 hover:text-indigo-900"
        @click="editMode = !editMode"
      >
        Edit
        <span class="sr-only">, {{ title }}</span>
      </button>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const props = defineProps({
  initialTitle: {
    type: String,
    default: null,
  },
  initialAuthor: {
    type: String,
    default: null,
  },
  initialYear: {
    type: String,
    default: null,
  },
  mediaType: {
    type: String,
    default: null,
  },
});

const title = ref(props.initialTitle);
const author = ref(props.initialAuthor);
const year = ref(Number(props.initialYear));
const editMode = ref(false);
</script>
