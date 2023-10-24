<template>
  <input
    v-if="props.field.name"
    :value="selectedResultId"
    :name="props.field.name"
    type="hidden"
  />
  <Combobox v-model="selectedResult" by="id">
    <div class="relative mt-1">
      <div
        class="relative w-full cursor-default overflow-hidden bg-white text-left rounded-md border-gray-300 shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm"
      >
        <ComboboxInput
          :id="props.field.id"
          class="w-full rounded-md border-gray-300 shadow-sm py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 focus:ring-0"
          :display-value="(result) => (result ? (result as Result).title : query)"
          @change="query = $event.target.value"
        />
        <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </ComboboxButton>
      </div>
      <TransitionRoot
        leave="transition ease-in duration-100"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <ComboboxOptions
          class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
        >
          <div
            v-if="results.length === 0 && query !== ''"
            class="relative cursor-default select-none py-2 px-4 text-gray-700"
          >
            Nothing found.
          </div>

          <ComboboxOption
            v-for="result in results"
            v-slot="{ selected, active }"
            :key="result.id"
            as="template"
            :value="result"
          >
            <li
              class="relative cursor-default select-none py-2 pl-10 pr-4"
              :class="{
                'bg-teal-600 text-white': active,
                'text-gray-900': !active,
              }"
            >
              <span
                class="block truncate"
                :class="{ 'font-medium': selected, 'font-normal': !selected }"
              >
                {{ result.autocomplete_label }}
              </span>
              <span
                v-if="selected"
                class="absolute inset-y-0 left-0 flex items-center pl-3"
                :class="{ 'text-white': active, 'text-teal-600': !active }"
              >
                <CheckIcon class="h-5 w-5" aria-hidden="true" />
              </span>
            </li>
          </ComboboxOption>
        </ComboboxOptions>
      </TransitionRoot>
    </div>
  </Combobox>
</template>

<script lang="ts" setup>
import { ref, watch, computed } from 'vue';
import type { PropType } from 'vue';
import {
  Combobox,
  ComboboxInput,
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
  TransitionRoot,
} from '@headlessui/vue';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid';
import type { VueFieldInterface } from '@/js/types';

import { createApiClient } from '@/js/utils/apiClient.ts';

type Result = {
  id: string;
  title: string;
  autocomplete_label: string;
};

const props = defineProps({
  // v-model bound to the id of the selectedResult.
  modelValue: {
    type: String as PropType<string | null>,
    default: null,
  },
  field: {
    type: Object as PropType<VueFieldInterface>,
    required: true,
  },
  // The url of the autocomplete endpoint to query for eligible results.
  url: {
    type: String as PropType<string>,
    default: null,
  },
  // The django csrfToken to authenticate queries to props.url.
  csrfToken: {
    type: String as PropType<string>,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue']);

const apiClient = createApiClient(props.csrfToken);

let query = ref('');
let results = ref<Array<Result>>([]);
let selectedResult = ref<Result | null>(null);

const selectedResultId = computed((): string => {
  if (selectedResult.value) {
    return selectedResult.value.id;
  } else {
    return '';
  }
});

// Query server for new results whenever the querystring changes.
watch(query, async () => {
  await getResults();
});

/**
 * Update root state with the id of the selected result.
 * We don't want to save the entire selectedResult in the state, only the id.
 * That id is also bound to a hidden input field. It will be bound to to the django
 * form field specified by props.html_name.
 */
watch(selectedResultId, (newValue) => {
  if (newValue) {
    emit('update:modelValue', newValue);
  } else {
    emit('update:modelValue', '');
  }
});

/**
 * Query the props.url autocomplete django view endpoint for elements that match the
 * query value.
 */
const getResults = async () => {
  const params = {
    q: query.value,
  };
  const res = await apiClient.get(props.url, { params });
  if (res) {
    results.value = res.data.results;
  }
};

/**
 * Fetch complete data for initial selected object.
 * @param id The UUID of the initial selected object.
 */
const getInitial = async (id: string) => {
  const params = {
    q: id,
  };
  const res = await apiClient.get(props.url, { params });
  if (res) {
    const responseResults = res.data.results;
    if (responseResults.length) {
      results.value = responseResults;
      selectedResult.value = responseResults[0];
    }
  }
};

watch(
  () => props.modelValue,
  async (newValue) => {
    if (props.modelValue !== selectedResultId.value) {
      if (!newValue) {
        // If modelValue is unset to "", then unset selectedResult
        selectedResult.value = null;
      } else {
        // If modelValue exists, then fetch it's selectedResult by id
        await getInitial(newValue);
      }
    }
  },
  { immediate: true },
);
</script>
