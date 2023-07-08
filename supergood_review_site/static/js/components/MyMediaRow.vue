<template>
  <tr class="align-top">
    <td
      class="w-full max-w-0 py-4 pr-3 text-sm font-medium text-gray-900 sm:w-auto sm:max-w-none sm:pl-0"
    >
      <!-- Title -->
      <div v-show="!editMode">
        {{ title }}
      </div>
      <div v-show="editMode" ref="titleFieldContainer">
        <slot name="title-field"></slot>
      </div>
      <!-- On smaller screens, collapse data into first column -->
      <dl class="font-normal space-y-2 lg:hidden">
        <!-- Creator (small screens) -->
        <div v-show="!editMode">
          <dt class="sr-only">Author</dt>
          <dd class="mt-1 truncate text-gray-700">{{ creator }}</dd>
        </div>
        <div v-show="editMode">
          <slot name="creator-field"></slot>
        </div>
        <!-- Year (small screens) -->
        <div class="sm:hidden">
          <div v-show="!editMode">
            <dt class="sr-only">Year</dt>
            <dd class="mt-1 truncate text-gray-500">{{ year }}</dd>
          </div>
          <div v-show="editMode">
            <slot name="year-field"></slot>
          </div>
        </div>
      </dl>
    </td>
    <!-- Creator (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 lg:table-cell">
      <div v-show="!editMode">
        {{ creator }}
      </div>
      <div v-show="editMode">
        <slot name="creator-field"></slot>
      </div>
    </td>
    <!-- Year (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">
      <div v-show="!editMode">
        {{ year }}
      </div>
      <div v-show="editMode">
        <slot name="year-field"></slot>
      </div>
    </td>
    <!-- Media Type -->
    <td class="px-3 py-4 text-sm text-gray-500 sm:table-cell">{{ mediaType }}</td>
    <!-- Edit Button -->
    <td class="py-4 sm:pl-3 text-right text-sm font-medium sm:pr-0">
      <button
        type="button"
        class="text-indigo-600 hover:text-indigo-900 align-top w-12"
        @click="editMode = !editMode"
      >
        <span v-show="editMode"> Cancel </span>
        <span v-show="!editMode"> Edit </span>
        <span class="sr-only">, {{ title }}</span>
      </button>
    </td>
  </tr>
  <tr v-show="editMode" class="border-none">
    <td class="flex justify-start pb-5 space-x-3">
      <!-- Submit Button -->
      <input
        type="submit"
        class="cursor-pointer inline-flex justify-center rounded-md bg-indigo-600 py-2 px-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        value="Submit"
      />
      <!-- Delete Button -->
      <input
        type="submit"
        class="cursor-pointer inline-flex justify-center rounded-md bg-red-600 py-2 px-3 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
        value="Delete"
      />
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, nextTick } from 'vue';

const props = defineProps({
  initialTitle: {
    type: String,
    default: null,
  },
  initialCreator: {
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
const creator = ref(props.initialCreator);
const year = ref(Number(props.initialYear));
const editMode = ref(false);
const titleFieldContainer = ref<HTMLElement | null>(null);

onMounted(() => {
  watch(editMode, (newValue) => {
    // Shift focus onto title-field once we enter editMode.
    if (newValue == true) {
      nextTick(() => {
        const titleFieldInput = titleFieldContainer?.value?.querySelector('input');
        titleFieldInput?.focus();
      });
    }
  });
});
</script>
