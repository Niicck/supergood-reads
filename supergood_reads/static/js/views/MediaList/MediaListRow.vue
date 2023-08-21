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
      <dl class="font-normal space-y-1 md:hidden">
        <!-- Creator (small screens) -->
        <div>
          <dt class="sr-only">Creator</dt>
          <dd class="mt-1 truncate text-gray-700">{{ props.creator }}</dd>
        </div>
        <!-- Actions (small screens) -->
        <div class="sm:hidden">
          <dd class="mt-1 truncate text-gray-700">
            <div class="flex flex-row space-x-3">
              <Button title="Write Review" />
              <Button title="Add to Wishlist" />
            </div>
          </dd>
        </div>
      </dl>
    </td>
    <!-- Creator (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 align-top md:table-cell">
      {{ props.creator }}
    </td>
    <!-- Actions (large screens) -->
    <td
      class="hidden px-3 py-4 text-sm text-gray-500 align-top text-right sm:table-cell"
    >
      <div class="flex flex-row justify-end space-x-3">
        <Button title="Write Review" />
        <Button title="Add to Wishlist" />
      </div>
    </td>
    <!-- Edit Button -->
    <td
      v-if="props.editableResults"
      class="py-4 text-right text-sm font-medium align-top sm:pr-0"
    >
      <Button title="Edit" /> <span class="sr-only">, {{ props.title }}</span>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { PropType } from 'vue';
import Button from '@/static/js/components/Button.vue';

const props = defineProps({
  id: { type: String as PropType<string>, required: true },
  title: { type: String as PropType<string>, required: true },
  year: { type: Number as PropType<number>, required: false },
  creator: { type: String as PropType<string>, required: false },
  icon: { type: String as PropType<string>, required: false },
  editableResults: { type: Boolean as PropType<boolean>, default: false },
});

console.log('~~~ thems props.editableResults?', props.editableResults);
</script>
