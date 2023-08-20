/* eslint vue/no-v-html: "off" */
<template>
  <tr class="align-text-top">
    <td
      class="w-full max-w-0 py-4 pr-3 text-sm font-medium text-gray-900 sm:w-auto sm:max-w-none sm:pl-0"
    >
      <!-- Title -->
      <div>
        <p class="flex flex-row items-center">
          <span class="pr-1" v-html="props.icon"></span>{{ props.title
          }}<span class="pl-1 text-gray-700">({{ props.year }})</span>
        </p>
      </div>
      <!-- On smaller screens, collapse data into first column -->
      <dl class="font-normal space-y-1 lg:hidden">
        <!-- Creator (small screens) -->
        <div>
          <dt class="sr-only">Creator</dt>
          <dd class="mt-1 truncate text-gray-700">{{ props.creator }}</dd>
        </div>
        <!-- CompletedAt (small screens) -->
        <div class="md:hidden">
          <dt class="sr-only">Completed at</dt>
          <dd class="mt-1 truncate text-gray-700">derp</dd>
        </div>
        <!-- Rating (small screens) -->
        <div class="sm:hidden">
          <dt class="sr-only">Rating</dt>
          <dd class="mt-1 truncate text-gray-500">derp</dd>
        </div>
      </dl>
    </td>
    <!-- Creator (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 align-top lg:table-cell">
      {{ props.creator }}
    </td>
    <!-- CompletedAt (large screens) -->
    <td
      class="hidden px-3 py-4 text-sm text-gray-500 align-top text-right md:table-cell"
    >
      derp
    </td>
    <!-- Rating (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 align-top sm:table-cell">derp</td>
    <!-- Edit Button -->
    <td class="py-4 sm:pl-3 text-right text-sm font-medium align-top sm:pr-0">
      <a
        type="button"
        class="text-indigo-600 hover:text-indigo-900 align-top w-12"
        href="#"
      >
        Edit <span class="sr-only">, Review of {{ props.title }}</span>
      </a>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { PropType } from 'vue';

const props = defineProps({
  id: { type: String as PropType<string>, required: true },
  title: { type: String as PropType<string>, required: true },
  year: { type: Number as PropType<number>, required: false },
  creator: { type: String as PropType<string>, required: false },
  icon: { type: String as PropType<string>, required: false },
});
</script>
