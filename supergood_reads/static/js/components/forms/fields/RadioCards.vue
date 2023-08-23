<template>
  <div>
    <input
      v-if="props.htmlName"
      :value="modelValue"
      :name="props.htmlName"
      type="hidden"
    />
    <RadioGroup
      :modelValue="modelValue"
      @update:modelValue="(newValue) => emit('update:modelValue', newValue)"
      class="mt-2"
    >
      <RadioGroupLabel :id="props.idForLabel" class="sr-only">
        {{ props.label }}
      </RadioGroupLabel>
      <div class="grid grid-cols-3 gap-3 lg:grid-cols-4">
        <RadioGroupOption
          v-for="choice in props.choices"
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
import type { Prop, PropType } from 'vue';
import type { FieldData } from '@/js/types';
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue';

const props = defineProps({
  // v-model bound to the id of the selectedResult.
  modelValue: {
    type: String,
    default: '',
  },
  // If you want this Field's value to be dynamically bound to a Form input named
  // "html_name".
  htmlName: {
    type: String as PropType<FieldData['htmlName']>,
    required: false,
  },
  choices: {
    type: Array as PropType<FieldData['choices']>,
    default: [],
  },
  idForLabel: {
    type: String as PropType<FieldData['idForLabel']>,
    default: '',
  },
  label: {
    type: String as PropType<FieldData['label']>,
    default: '',
  },
});

const emit = defineEmits(['update:modelValue']);
</script>
