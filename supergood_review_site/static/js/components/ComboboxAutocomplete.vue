<template>
  <input v-model="store[stateKey]" type="hidden" :name="fieldData.html_name" />
  <Combobox v-model="selectedResult" by="id">
    <div class="relative mt-1">
      <div
        class="relative w-full cursor-default overflow-hidden bg-white text-left rounded-md border-gray-300 shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm"
      >
        <ComboboxInput
          class="w-full rounded-md border-gray-300 shadow-sm py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 focus:ring-0"
          :display-value="(result) => (result ? result.title : query)"
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
          class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
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
                {{ result.display_name }}
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
import { ref, watch, onMounted } from 'vue';
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
import axios from 'axios';
import type { State } from '@/static/js/stores';
import type { FieldData } from '@/static/js/types';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';

type Result = {
  id: string;
  title: string;
  display_name: string;
};

const props = defineProps({
  /**
   * The element from the pinia store's State that you want to be bound to the Combobox
   * selectedResult.id.
   */
  stateKey: {
    type: String as PropType<keyof State>,
    default: null,
  },
  /**
   * The id attribute of the <script> element where the django field's metadata was
   * was stored as an output of the django json_script filter.
   */
  fieldDataJsonScriptId: {
    type: String,
    default: null,
  },
  /**
   * The url of the autocomplete endpoint to query for eligible results.
   */
  url: {
    type: String,
    default: null,
  },
  /**
   * The django csrfToken to authenticate queries to props.url.
   */
  csrfToken: {
    type: String,
    default: '',
  },
});

const fieldData = ref<FieldData>({
  html_name: '',
  label: '',
  id_for_label: '',
  choices: [],
});
let query = ref('');
let results = ref<Array<Result>>([]);
let selectedResult = ref<Result | null>(null);

const store = window.store;

// Query server for new results whenever the querystring changes.
watch(query, () => {
  getResults();
});

/**
 * Update root state with the id of the selected result.
 * We don't want to save the entire selectedResult in the state, only the id.
 * That id is also bound to a hidden input field. It will be bound to to the django
 * form field specified by fieldData.html_name.
 */
watch(selectedResult, (newValue) => {
  if (newValue) {
    store[props.stateKey] = newValue.id;
  } else {
    store[props.stateKey] = '';
  }
});

/**
 * Retrieve the fieldData value from the json data embedded into a <script> tag by the
 * json_script django filter.
 */
onMounted(() => {
  fieldData.value = parseJsonScriptFilter(props.fieldDataJsonScriptId) as FieldData;
});

/**
 * Query the props.url autocomplete django view endpoint for elements that match the
 * query value.
 */
const getResults = () => {
  return axios({
    method: 'get',
    url: props.url,
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
    })
    .catch((error) => {
      console.log('Error:', error);
    });
};
</script>
