<!-- eslint-disable vue/no-v-html -->
<template>
  <tr class="align-text-top">
    <td
      class="w-full max-w-0 py-4 pr-3 text-sm font-medium text-gray-900 sm:w-auto sm:max-w-none sm:pl-0"
    >
      <!-- Title -->
      <div>
        <p class="flex flex-row items-center">
          <span class="pr-1" v-html="props.icon"></span>
          <span
            >{{ props.title
            }}<span class="text-gray-700"> ({{ props.year }})</span></span
          >
        </p>
      </div>
      <!-- On smaller screens, collapse data into first column -->
      <dl class="font-normal space-y-3 lg:hidden">
        <!-- Creator (small screens) -->
        <div class="lg:hidden">
          <dt class="sr-only">Creator</dt>
          <dd class="text-gray-700">{{ props.creator }}</dd>
        </div>
        <!-- Genres (small screens) -->
        <div class="md:hidden">
          <dt class="sr-only">Genres</dt>
          <dd class="text-gray-700">
            <GenreCell
              :genres="genres"
              :selected-genres="selectedGenres"
              @toggle-checked-genre="toggleSelectedGenre"
            />
          </dd>
        </div>
        <!-- Actions (small screens) -->
        <div class="sm:hidden">
          <dd class="truncate text-gray-700">
            <div class="flex flex-row space-x-3">
              <DefaultButton title="Write Review" />
              <DefaultButton title="Add to Wishlist" />
              <DefaultButton
                v-if="props.updateUrl"
                title="Edit"
                @click="navigateToEditPage"
              />
            </div>
          </dd>
        </div>
      </dl>
    </td>
    <!-- Creator (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 align-top lg:table-cell">
      {{ props.creator }}
    </td>
    <!-- Genre (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 align-top md:table-cell">
      <div class="space-y-1">
        <GenreCell
          :genres="genres"
          :selected-genres="selectedGenres"
          @toggle-checked-genre="toggleSelectedGenre"
        />
      </div>
    </td>
    <!-- Actions (large screens) -->
    <td
      class="hidden px-3 py-4 text-sm text-gray-500 align-top text-right sm:table-cell"
    >
      <div class="flex flex-row justify-end space-x-3 whitespace-nowrap">
        <DefaultButton title="Write Review" />
        <DefaultButton title="Add to Wishlist" />
        <DefaultButton
          v-if="props.updateUrl"
          title="Edit"
          @click="navigateToEditPage"
        />
      </div>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { PropType } from 'vue';
import DefaultButton from '@/js/components/DefaultButton.vue';
import GenreCell from '@/js/views/Library/GenreCell.vue';

const props = defineProps({
  id: { type: String as PropType<string>, required: true },
  title: { type: String as PropType<string>, required: true },
  year: { type: Number as PropType<number | null>, default: null },
  creator: { type: String as PropType<string>, default: '' },
  icon: { type: String as PropType<string>, default: '' },
  genres: { type: Array as PropType<string[]>, default: () => [] },
  updateUrl: { type: String as PropType<string>, default: '' },
  selectedGenres: { type: Array as PropType<string[]>, required: true },
});

const emit = defineEmits(['toggle-checked-genre']);

const toggleSelectedGenre = (genre: string) => {
  emit('toggle-checked-genre', genre);
};

const navigateToEditPage = () => {
  window.location.href = props.updateUrl;
};
</script>

<style>
.selected-genre {
  @apply bg-indigo-600 text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600;
}
</style>
