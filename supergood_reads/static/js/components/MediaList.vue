<template>
  <div class="px-0">
    <div class="flex flex-1">
      <div class="w-full max-w-lg">
        <label for="search" class="sr-only">Search</label>
        <div class="relative text-gray-400 focus-within:text-gray-600">
          <div
            class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3"
          >
            <MagnifyingGlassIcon class="h-5 w-5" aria-hidden="true" />
          </div>
          <input
            @input="query = $event.target.value"
            id="search"
            class="block w-full max-w-lg rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-1.5 pl-10 pr-3 text-gray-900 sm:leading-6"
            placeholder="Search"
            type="search"
            name="search"
          />
        </div>
      </div>
    </div>
    <div class="mt-8">
      <table v-if="results" class="table-fixed min-w-full divide-y divide-gray-300">
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
              class="hidden px-3 py-3.5 text-right text-sm font-semibold text-gray-900 md:table-cell w-28"
            >
              Completed
            </th>
            <th
              scope="col"
              class="hidden px-3 py-3.5 text-left text-sm font-semibold text-gray-900 sm:table-cell"
            >
              Rating
            </th>
            <th scope="col" class="py-3.5 sm:pl-2 sm:pr-0">
              <span class="sr-only">Edit</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <template v-for="result in results">
            <MediaListRow v-bind="result" />
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
import MediaListRow from '@/static/js/components/MediaListRow.vue';

let searchAbortController: AbortController | null = null;

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

const query = ref('');
const pagination: Ref<Pagination | null> = ref(null);
const results = ref([]);
const page = ref(1);

const nextPage = () => {
  const nextPageNumber = pagination?.value?.nextPageNumber;
  if (nextPageNumber) {
    page.value = nextPageNumber;
  }
};

const previousPage = () => {
  const previousPageNumber = pagination?.value?.previousPageNumber;
  if (pagination && previousPageNumber) {
    page.value = previousPageNumber;
  }
};

watch(query, () => {
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
      console.log(res.data);
    })
    .catch((error) => {
      if (!(error.name === 'CanceledError')) {
        console.log('Error:', error);
      }
    });
};
</script>
