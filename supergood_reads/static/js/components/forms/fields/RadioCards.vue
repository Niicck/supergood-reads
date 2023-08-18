<template>
  <div>
    <input v-model="store[stateKey]" type="hidden" :name="props.fieldData.html_name" />
    <RadioGroup v-model="store[stateKey]" class="mt-2">
      <RadioGroupLabel class="sr-only"> {{ props.fieldData.label }} </RadioGroupLabel>
      <div class="grid grid-cols-3 gap-3 lg:grid-cols-4">
        <RadioGroupOption
          v-for="choice in props.fieldData.choices"
          :key="choice[0]"
          v-slot="{ active, checked }"
          as="template"
          :value="choice[0]"
        >
          <div
            :class="[
              'cursor-pointer focus:outline-none',
              active ? 'ring-2 ring-indigo-600 ring-offset-2' : '',
              checked
                ? 'bg-indigo-600 text-white hover:bg-indigo-500'
                : 'ring-1 ring-inset ring-gray-300 bg-white text-gray-900 hover:bg-gray-50',
              'flex items-center justify-center rounded-md py-3 px-3 text-sm font-semibold capitalize sm:flex-1',
            ]"
          >
            <RadioGroupLabel as="span">{{ choice[1] }}</RadioGroupLabel>
          </div>
        </RadioGroupOption>
      </div>
    </RadioGroup>
  </div>
</template>

<script lang="ts" setup>
import type { PropType } from 'vue';
import type { State } from '@/static/js/stores';
import type { FieldData } from '@/static/js/types';
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue';

const props = defineProps({
  /**
   * The element from the pinia store's State that you want to be bound to the selected
   * value of the RadioGroup.
   */
  stateKey: {
    type: String as PropType<keyof State>,
    default: null,
  },
  /**
   * The id attribute of the <script> element where the django field's metadata was
   * was stored as an output of the django json_script filter.
   */
  fieldData: {
    type: Object as PropType<FieldData>,
    required: true,
  },
});

const store = window.store;
</script>
