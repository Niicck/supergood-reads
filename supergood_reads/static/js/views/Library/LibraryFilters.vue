<template>
  <section aria-labelledby="filter-heading">
    <h2 id="filter-heading" class="sr-only">Filters</h2>
    <div>
      <div class="">
        <div class="flow-root">
          <PopoverGroup class="flex items-center divide-x space-x-4 divide-gray-200">
            <Popover
              v-for="(filter, sectionIdx) in filters"
              :key="filter.name"
              class="relative inline-block text-left first:pl-0 sm:first:pl-4 pl-4"
            >
              <PopoverButton
                class="group inline-flex justify-center text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                <span>{{ filter.name }}</span>
                <span
                  v-if="getCheckedCount(filter)"
                  class="ml-1.5 rounded bg-gray-200 px-1.5 py-0.5 text-xs font-semibold tabular-nums text-gray-700"
                >
                  {{ getCheckedCount(filter) }}
                </span>
                <ChevronDownIcon
                  class="-mr-1 ml-1 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500"
                  aria-hidden="true"
                />
              </PopoverButton>
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <PopoverPanel
                  class="absolute left-0 sm:left-auto sm:right-0 z-10 mt-2 origin-top-left sm:origin-top-right rounded-md bg-white p-4 shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none"
                >
                  <form class="space-y-4">
                    <button
                      v-if="filter.clear && getCheckedCount(filter)"
                      @click="clearFilter(filter.id)"
                      class="rounded bg-white px-2 py-1 text-sm font-medium text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 flex flex-row"
                    >
                      <span>Clear Selected</span
                      ><span
                        ><XMarkIcon class="h-5 w-5 text-red-500" aria-hidden="true"
                      /></span>
                    </button>
                    <div
                      v-for="(option, optionIdx) in filter.options"
                      :key="option.value"
                      class="flex items-center"
                    >
                      <input
                        :id="`filter-${filter.id}-${optionIdx}`"
                        :name="`${filter.id}[]`"
                        :value="option.value"
                        type="checkbox"
                        :checked="option.checked"
                        @input="toggleCheckedOption(filter.id, option.value)"
                        class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <label
                        :for="`filter-${filter.id}-${optionIdx}`"
                        class="ml-3 whitespace-nowrap pr-6 text-sm font-medium text-gray-900"
                        >{{ option.label }}</label
                      >
                    </div>
                  </form>
                </PopoverPanel>
              </transition>
            </Popover>
          </PopoverGroup>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { Popover, PopoverButton, PopoverGroup, PopoverPanel } from '@headlessui/vue';
import { ChevronDownIcon, XMarkIcon } from '@heroicons/vue/20/solid';
import type { Filter } from '@/js/types';

const { filters } = defineProps({
  filters: {
    type: Array<Filter>,
    required: true,
  },
});

const emit = defineEmits(['toggle-checked-option', 'clear-filter']);

const toggleCheckedOption = (filterId: string, optionValue: string) => {
  emit('toggle-checked-option', filterId, optionValue);
};

const clearFilter = (filterId: string) => {
  emit('clear-filter', filterId);
};

const getCheckedCount = (filter: Filter) => {
  return filter.options.filter((f) => f.checked).length;
};
</script>
