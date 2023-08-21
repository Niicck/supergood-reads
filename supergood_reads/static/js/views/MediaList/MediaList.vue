<template>
  <div class="px-0">
    <div class="flex flex-1 flex-col space-y-3">
      <div class="w-full max-w-lg">
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
            >Show Editable Only</label
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
              class="hidden px-3 py-3.5 text-left text-sm font-semibold text-gray-900 lg:table-cell"
            >
              Creator
            </th>
            <th
              scope="col"
              class="hidden pl-3 py-3.5 text-right text-sm font-semibold text-gray-900 md:table-cell"
            >
              <span class="sr-only">Actions</span>
            </th>
            <th v-if="showEditableOnly" scope="col" class="py-3.5">
              <span class="sr-only">Edit</span>
            </th>
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
import { ref, onMounted, watch } from 'vue';
import type { Ref } from 'vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/20/solid';
import axios from 'axios';
import Pagination from '@/static/js/components/Pagination.vue';
import MediaListRow from '@/static/js/views/MediaList/MediaListRow.vue';

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
    default: '',
  },
  csrfToken: {
    type: String,
    default: '',
  },
});

let searchAbortController: AbortController | null = null;

const query = ref('');
const pagination: Ref<Pagination | null> = ref(null);
const results = ref([]);
const page = ref(1);
const showEditableOnly = ref(false);
const editableResults = ref(false);
const tableTop: Ref<HTMLElement | null> = ref(null);

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

watch([query, showEditableOnly], () => {
  page.value = 1;
  search();
});

watch(page, () => {
  search();
});

onMounted(() => {
  search();
});

const search = () => {
  console.log('q=', query.value);

  // Abort previous request if it's still in progress
  if (searchAbortController) {
    searchAbortController.abort();
  }
  // Create a new AbortController for this request
  searchAbortController = new AbortController();

  return axios({
    method: 'get',
    url: props.searchUrl,
    params: {
      q: query.value,
      page: page.value,
      showEditableOnly: showEditableOnly.value,
    },
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': props.csrfToken,
    },
    signal: searchAbortController.signal,
  })
    .then((res) => {
      results.value = res.data.results;
      pagination.value = res.data.pagination;
      editableResults.value = showEditableOnly.value;
      console.log(res.data);
    })
    .catch((error) => {
      if (!(error.name === 'CanceledError')) {
        console.log('Error:', error);
      }
    });
};
</script>
