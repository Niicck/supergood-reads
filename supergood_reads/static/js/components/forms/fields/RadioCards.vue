<template>
  <div>
    <input
      v-if="props.field.name"
      :value="selectedValue"
      :name="props.field.name"
      type="hidden"
    />
    <RadioGroup v-model="selectedValue" :disabled="props.disabled" class="mt-2">
      <RadioGroupLabel class="sr-only">
        {{ props.field.label }}
      </RadioGroupLabel>
      <div class="grid grid-cols-3 gap-3 lg:grid-cols-4">
        <RadioGroupOption
          v-for="choice in choices"
          :key="choice[0]"
          v-slot="{ active, checked }"
          :value="choice[0]"
          as="template"
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
import { ref, computed, watch } from 'vue';
import type { PropType } from 'vue';
import type { VueFieldInterface } from '@/js/types';
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue';

const props = defineProps({
  // v-model bound to the value of the selectedResult.
  modelValue: {
    type: [String, Number] as PropType<string | number | null>,
    default: null,
  },
  field: {
    type: Object as PropType<VueFieldInterface>,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

const choices = computed((): (string | number)[][] => {
  // if field.choices is a dumped JSON string, then parse it
  if (typeof props.field.choices === 'string') {
    return JSON.parse(props.field.choices);
  }
  return props.field.choices || [];
});

// Bind selectedValue to the optional v-model, or set it to the initialValue of
// the field.
const selectedValue = ref(props.modelValue || props.field.initialValue);

// Update local selectedValue when v-model changes.
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== null) {
      selectedValue.value = newValue;
    }
  },
);

// If bound to a v-model, update it when the selectedValue changes.
watch(selectedValue, (newValue) => {
  emit('update:modelValue', newValue);
});
</script>
