<template>
  <div>
    <RadioGroup name="{{ fieldData.name }}" class="mt-2">
      <RadioGroupLabel class="sr-only"> {{ fieldData.label }} </RadioGroupLabel>
      <div class="grid grid-cols-3 gap-3 sm:grid-cols-6">
        <RadioGroupOption
          v-for="choice in fieldData.choices"
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
              'flex items-center justify-center rounded-md py-3 px-3 text-sm font-semibold uppercase sm:flex-1',
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
import { ref, onMounted } from 'vue';
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue';
import { parseJsonScriptFilter } from '@/static/js/utils/parseJsonScriptFilter';

type FieldData = {
  name: string;
  label: string;
  choices: Array<Array<string | number | boolean>>;
};

const props = defineProps({
  selectedMediaTypeObjectId: {
    type: String,
    default: null,
  },
  jsonScriptId: {
    type: String,
    default: null,
  },
});

const fieldData = ref<FieldData>({
  name: '',
  label: '',
  choices: [],
});

const emit = defineEmits(['update:modelValue']);

onMounted(() => {
  fieldData.value = parseJsonScriptFilter(props.jsonScriptId) as FieldData;
});
</script>
