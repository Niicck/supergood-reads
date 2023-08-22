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
              v-model="query"
              id="search"
              class="block w-full max-w-lg rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-1.5 pl-10 pr-3 text-gray-900 sm:leading-6"
              placeholder="Search"
              type="search"
              name="search"
              autocomplete="off"
            />
          </div>
        </div>
        <!-- Filters -->
        <MediaListFilters
          :filters="filters"
          @toggle-checked-option="toggleCheckedFilterOption"
        />
      </div>
      <!-- Editable Checkbox -->
      <div class="relative flex items-start">
        <div class="flex h-6 items-center">
          <input
            v-model="showEditableOnly"
            id="my-media-only"
            aria-describedby="my-media-only-description"
            name="my-media-only"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
          />
        </div>
        <div class="ml-3 text-sm leading-6">
          <label for="my-media-only" class="font-medium text-gray-900"
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
              class="py-3.5 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0"
            >
              Title
            </th>
            <th
              scope="col"
              class="hidden px-3 py-3.5 text-left text-sm font-semibold text-gray-900 md:table-cell"
            >
              Creator
            </th>
            <th
              scope="col"
              class="hidden pl-3 py-3.5 text-right text-sm font-semibold text-gray-900 sm:table-cell"
            >
              <span class="sr-only">Actions</span>
            </th>
            <th v-if="showEditableOnly" scope="col" class="py-3.5">
              <span class="sr-only">Edit</span>
            </th>
            <th v-else></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <template v-for="result in results">
            <MediaListRow v-bind="result" :editableResults="editableResults" />
          </template>
        </tbody>
      </table>
      <Pagination
        v-if="pagination"
        v-bind="pagination"
        @next="nextPage"
        @previous="previousPage"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, watch, computed } from 'vue';
import type { Ref } from 'vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/20/solid';
import _ from 'lodash';

import type { Filter, FilterOption } from '@/js/types';
import Pagination from '@/js/components/Pagination.vue';
import MediaListRow from '@/js/views/MediaList/MediaListRow.vue';
import MediaListFilters from '@/js/views/MediaList/MediaListFilters.vue';
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
  countriesApiUrl: {
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
const results = ref([]);
const page = ref(1);
const showEditableOnly = ref(false);
const editableResults = ref(false);
const tableTop: Ref<HTMLElement | null> = ref(null);

const genreFilterId = 'genre';
const countryFilterId = 'country';
const mediaTypeFilterId = 'media_type';

const filters: Ref<Filter[]> = ref([
  {
    id: mediaTypeFilterId,
    name: 'Media Type',
    options: [],
  },
  {
    id: genreFilterId,
    name: 'Genre',
    options: [],
  },
  {
    id: countryFilterId,
    name: 'Country',
    options: [],
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

const getFilter = (filterId: string) => filters.value.find((f) => f.id === filterId);
const getSelectedOptions = (filterId: string) => {
  const foundFilter = getFilter(filterId);
  if (foundFilter) {
    return foundFilter.options.filter((o) => o.checked).map((o) => o.value);
  }
  return [];
};
const selectedGenres = computed(() => getSelectedOptions(genreFilterId));
const selectedCountries = computed(() => getSelectedOptions(countryFilterId));
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
  if (pagination && previousPageNumber) {
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
    selectedCountries.value,
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
  await Promise.all([search(), getMediaTypeChoices(), getGenres(), getCountries()]);
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
    countries: selectedCountries.value,
    media_types: selectedMediaTypes.value,
  };
  const res = await apiClient.get(props.searchUrl, {
    params,
    signal: searchAbortController.signal,
  });
  if (res) {
    results.value = res.data.results;
    pagination.value = res.data.pagination;
    editableResults.value = showEditableOnly.value;
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

const getCountries = async () => {
  const res = await apiClient.get(props.countriesApiUrl);
  if (res) {
    const countryFilter = getFilter(countryFilterId);
    if (countryFilter) {
      countryFilter.options = res.data.map((r): FilterOption => {
        return { label: r.name, value: r.name, checked: false };
      });
    }
  }
};
</script>
