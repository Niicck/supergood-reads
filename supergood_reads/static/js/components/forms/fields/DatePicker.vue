<!-- eslint-disable vue/no-v-html -->
<template>
  <div class="mt-5">
    <div>
      <div v-if="props.dayField.errorsHtml" v-html="props.dayField.errorsHtml"></div>
      <div
        v-if="props.monthField.errorsHtml"
        v-html="props.monthField.errorsHtml"
      ></div>
      <div v-if="props.yearField.errorsHtml" v-html="props.yearField.errorsHtml"></div>
    </div>
    <div class="mt-1 sm:mt-0 flex flex-wrap items-end gap-4">
      <div>
        <label
          :for="props.dayField.id"
          class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5"
        >
          {{ props.dayField.label }}
        </label>
        <select
          :id="props.dayField.id"
          v-model="day"
          :name="props.dayField.name"
          class="block w-fit rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:max-w-xs sm:text-sm"
        >
          >
          <option
            v-for="([value, name], idx) in props.dayField.choices"
            :key="idx"
            :value="value"
          >
            {{ name }}
          </option>
        </select>
      </div>
      <div>
        <label
          :for="props.monthField.id"
          class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5"
        >
          {{ props.monthField.label }}
        </label>
        <select
          :id="props.monthField.id"
          v-model="month"
          :name="props.monthField.name"
          class="block w-fit rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:max-w-xs sm:text-sm"
        >
          >
          <option
            v-for="([value, name], idx) in props.monthField.choices"
            :key="idx"
            :value="value"
          >
            {{ name }}
          </option>
        </select>
      </div>
      <div>
        <label
          :for="props.yearField.id"
          class="block text-sm font-medium leading-6 text-gray-900 sm:pt-1.5"
        >
          {{ props.yearField.label }}
        </label>
        <input
          :id="props.yearField.id"
          v-model="year"
          :name="props.yearField.name"
          class="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:max-w-xs sm:text-sm"
          type="number"
        />
      </div>
      <div class="w-min">
        <VueDatePicker
          auto-apply
          input-class-name="dp-custom-input"
          menu-class-name="dp-custom-menu"
          :format="() => '_'"
          :clearable="false"
          :enable-time-picker="false"
          :max-date="new Date()"
          :model-value="date"
          @update:model-value="setDate"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import type { PropType } from 'vue';
import type { VueFieldInterface } from '@/js/types';
import { safeParseInt } from '@/js/utils/safeParseInt';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const props = defineProps({
  dayField: {
    type: Object as PropType<VueFieldInterface>,
    required: true,
  },
  monthField: {
    type: Object as PropType<VueFieldInterface>,
    required: true,
  },
  yearField: {
    type: Object as PropType<VueFieldInterface>,
    required: true,
  },
});

const day = ref(props.dayField.initialValue);
const month = ref(props.monthField.initialValue);
const year = ref(props.yearField.initialValue);

const date = computed((): Date | null => {
  const yearInt = safeParseInt(year.value);
  const monthInt = safeParseInt(month.value);
  const dayInt = safeParseInt(day.value);
  if (yearInt && monthInt && dayInt) {
    return new Date(yearInt, monthInt - 1, dayInt);
  } else {
    return null;
  }
});

const setDate = (newValue: Date | null) => {
  if (newValue) {
    day.value = newValue.getDate();
    month.value = newValue.getMonth() + 1;
    year.value = newValue.getFullYear();
  } else {
    day.value = '';
    month.value = '';
    year.value = '';
  }
};
</script>

<style>
.dp-custom-input {
  @apply py-2 px-5 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:max-w-xs sm:text-sm;
}
</style>
