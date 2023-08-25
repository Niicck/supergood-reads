<template>
  <div class="px-0">
    <div class="flex flex-1 flex-col space-y-3">
      <div class="w-full flex flex-col sm:flex-row space-y-3 sm:space-y-0">
        <!-- Search -->
        <div class="flex-1 max-w-lg">
          <label for="search" class="sr-only">Search</label>
          <div class="relative text-gray-400 focus-within:text-gray-600">
            <div
              class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3"
            >
              <MagnifyingGlassIcon class="h-5 w-5" aria-hidden="true" />
            </div>
            <input
              id="search"
              v-model="query"
              class="block w-full max-w-lg rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-1.5 pl-10 pr-3 text-gray-900 sm:leading-6"
              placeholder="Search"
              type="search"
              name="search"
              autocomplete="off"
            />
          </div>
        </div>
        <!-- Filters -->
        <LibraryFilters
          :filters="filters"
          @toggle-checked-option="toggleCheckedFilterOption"
          @clear-filter="clearFilter"
        />
      </div>
      <!-- Editable Checkbox -->
      <div class="relative flex items-start">
        <div class="flex h-6 items-center">
          <input
            id="library-only"
            v-model="showEditableOnly"
            aria-describedby="library-only-description"
            name="library-only"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
          />
        </div>
        <div class="ml-3 text-sm leading-6">
          <label for="library-only" class="font-medium text-gray-900"
            >Show Editable Titles Only</label
          >
        </div>
      </div>
    </div>
    <div class="mt-8">
      <table
        v-if="results"
        ref="tableTop"
        class="table-fixed min-w-full divide-y divide-gray-300"
      >
        <thead>
          <tr>
            <th
              scope="col"
              class="py-3.5 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0 w-96"
            >
              Title
            </th>
            <th
              scope="col"
              class="hidden px-3 py-3.5 text-left text-sm font-semibold text-gray-900 lg:table-cell w-64"
            >
              Creator
            </th>
            <th
              scope="col"
              class="hidden px-3 py-3.5 text-left text-sm font-semibold text-gray-900 md:table-cell"
            >
              Genre
            </th>
            <th
              scope="col"
              class="hidden pl-3 py-3.5 text-right text-sm font-semibold text-gray-900 sm:table-cell"
            >
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <template v-for="result in results" :key="result.id">
            <LibraryRow
              v-bind="result"
              :selected-genres="selectedGenres"
              @toggle-checked-genre="
                (optionValue: string) => toggleCheckedFilterOption(genreFilterId, optionValue)
              "
            />
          </template>
        </tbody>
      </table>
      <PaginationNav
        v-if="pagination"
        v-bind="pagination"
        @next="nextPage"
        @previous="previousPage"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue';
import type { Ref } from 'vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/20/solid';
import _ from 'lodash';

import type { Filter, FilterOption, MediaSearchResult } from '@/js/types';
import PaginationNav from '@/js/components/PaginationNav.vue';
import LibraryRow from '@/js/views/Library/LibraryRow.vue';
import LibraryFilters from '@/js/views/Library/LibraryFilters.vue';
import { createApiClient } from '@/js/utils/apiClient.ts';

type Pagination = {
  hasNext: boolean;
  hasPrevious: boolean;
  nextPageNumber: number | null;
  previousPageNumber: number | null;
  startIndex: number;
  endIndex: number;
  count: number;
};

const props = defineProps({
  searchUrl: {
    type: String,
    required: true,
  },
  genresApiUrl: {
    type: String,
    required: true,
  },
  mediaTypeChoicesApiUrl: {
    type: String,
    required: true,
  },
  csrfToken: {
    type: String,
    required: true,
  },
});

const apiClient = createApiClient(props.csrfToken);
let searchAbortController: AbortController | null = null;

const query = ref('');
const pagination: Ref<Pagination | null> = ref(null);
const results: Ref<MediaSearchResult[]> = ref([]);
const page = ref(1);
const showEditableOnly = ref(false);
const tableTop: Ref<HTMLElement | null> = ref(null);

const genreFilterId = 'genre';
const mediaTypeFilterId = 'media_type';

const filters: Ref<Filter[]> = ref([
  {
    id: mediaTypeFilterId,
    name: 'Media Type',
    options: [],
    clear: false,
  },
  {
    id: genreFilterId,
    name: 'Genre',
    options: [],
    clear: true,
  },
]);

const toggleCheckedFilterOption = (filterId: string, optionValue: string) => {
  const foundFilter = getFilter(filterId);
  if (foundFilter) {
    const foundOption = foundFilter.options.find((o) => o.value == optionValue);
    if (foundOption) {
      foundOption.checked = !foundOption.checked;
    }
  }
};

const clearFilter = (filterId: string) => {
  const foundFilter = getFilter(filterId);
  if (foundFilter) {
    foundFilter.options.forEach((o) => (o.checked = false));
  }
};

const getFilter = (filterId: string) => filters.value.find((f) => f.id === filterId);
const getSelectedOptions = (filterId: string) => {
  const foundFilter = getFilter(filterId);
  if (foundFilter) {
    return foundFilter.options.filter((o) => o.checked).map((o) => o.value);
  }
  return [];
};
const selectedGenres = computed(() => getSelectedOptions(genreFilterId));
const selectedMediaTypes = computed(() => getSelectedOptions(mediaTypeFilterId));

const nextPage = () => {
  const nextPageNumber = pagination?.value?.nextPageNumber;
  if (nextPageNumber) {
    page.value = nextPageNumber;
    if (tableTop.value) {
      tableTop.value.scrollIntoView();
    }
  }
};

const previousPage = () => {
  const previousPageNumber = pagination?.value?.previousPageNumber;
  if (pagination.value && previousPageNumber) {
    page.value = previousPageNumber;
    if (tableTop.value) {
      tableTop.value.scrollIntoView();
    }
  }
};

// Return array in WatchSource function so that searches are only triggered if the
// actual selected values within each filter change.
watch(
  () => [
    query.value,
    showEditableOnly.value,
    selectedGenres.value,
    selectedMediaTypes.value,
  ],
  async (oldValue, newValue) => {
    if (!_.isEqual(oldValue, newValue)) {
      if (page.value !== 1) {
        page.value = 1; // This will trigger a search()
      } else {
        await search();
      }
    }
  },
);

watch(page, async () => {
  await search();
});

onMounted(async () => {
  await Promise.all([search(), getMediaTypeChoices(), getGenres()]);
});

const search = async () => {
  // Abort previous request if it's still in progress
  if (searchAbortController) {
    searchAbortController.abort();
  }
  // Create a new AbortController for this request
  searchAbortController = new AbortController();

  const params = {
    q: query.value,
    page: page.value,
    showEditableOnly: showEditableOnly.value,
    genres: selectedGenres.value,
    media_types: selectedMediaTypes.value,
  };
  const res = await apiClient.get(props.searchUrl, {
    params,
    signal: searchAbortController.signal,
  });
  if (res) {
    results.value = res.data.results;
    pagination.value = res.data.pagination;
  }
};

const getMediaTypeChoices = async () => {
  const res = await apiClient.get(props.mediaTypeChoicesApiUrl);
  if (res) {
    const mediaTypeFilter = getFilter(mediaTypeFilterId);
    if (mediaTypeFilter) {
      mediaTypeFilter.options = res.data.map((r): FilterOption => {
        return { label: r.name, value: r.id, checked: true };
      });
    }
  }
};

const getGenres = async () => {
  const res = await apiClient.get(props.genresApiUrl);
  if (res) {
    const genreFilter = getFilter(genreFilterId);
    if (genreFilter) {
      genreFilter.options = res.data.map((r): FilterOption => {
        return { label: r.name, value: r.name, checked: false };
      });
    }
  }
};
</script>
