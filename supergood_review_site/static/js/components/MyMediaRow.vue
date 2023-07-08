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
      <dl class="font-normal lg:hidden">
        <!-- Creator (small screens) -->
        <div v-show="!editMode">
          <dt class="sr-only">Author</dt>
          <dd class="mt-1 truncate text-gray-700">{{ creator }}</dd>
        </div>
        <div v-show="editMode">
          <slot name="creator-field"></slot>
        </div>
        <!-- Year (small screens) -->
        <div v-show="!editMode">
          <dt class="sr-only sm:hidden">Year</dt>
          <dd class="mt-1 truncate text-gray-500 sm:hidden">{{ year }}</dd>
        </div>
        <div v-show="editMode">
          <slot name="year-field"></slot>
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
    <!-- MediaType -->
    <td class="px-3 py-4 text-sm text-gray-500 sm:table-cell">{{ mediaType }}</td>
    <td class="py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
      <button
        type="button"
        class="text-indigo-600 hover:text-indigo-900 align-top"
        @click="editMode = !editMode"
      >
        Edit
        <span class="sr-only">, {{ title }}</span>
      </button>
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
