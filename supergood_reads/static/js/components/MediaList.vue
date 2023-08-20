<template>
  <div class="px-4 sm:px-0">
    <div class="flex flex-1 justify-center px-2 lg:ml-6 lg:justify-end">
      <div class="w-full max-w-lg lg:max-w-xs">
        <label for="search" class="sr-only">Search</label>
        <div class="relative text-gray-400 focus-within:text-gray-600">
          <div
            class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3"
          >
            <MagnifyingGlassIcon class="h-5 w-5" aria-hidden="true" />
          </div>
          <input
            @change="query = $event.target.value"
            id="search"
            class="block w-full rounded-md border-0 bg-white py-1.5 pl-10 pr-3 text-gray-900 focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600 sm:text-sm sm:leading-6"
            placeholder="Search"
            type="search"
            name="search"
          />
        </div>
      </div>
    </div>
    <div class="-mx-4 mt-8 sm:-mx-0">
      <table class="table-fixed min-w-full divide-y divide-gray-300">
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
            <MediaListRow />
          </template>
        </tbody>
      </table>
      <Pagination v-if="pagination" v-bind="pagination" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/20/solid';
import axios from 'axios';
import Pagination from '@/static/js/components/Pagination.vue';
import MediaListRow from '@/static/js/components/MediaListRow.vue';

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
const pagination = ref({});
const results = ref([]);

watch(query, () => {
  search();
});

onMounted(() => {
  search();
});

const search = () => {
  return axios({
    method: 'get',
    url: props.searchUrl,
    params: {
      q: query.value,
    },
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': props.csrfToken,
    },
  })
    .then((res) => {
      results.value = res.data.results;
      pagination.value = res.data.pagination;
    })
    .catch((error) => {
      console.log('Error:', error);
    });
};
</script>
