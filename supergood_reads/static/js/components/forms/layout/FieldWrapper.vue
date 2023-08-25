<!-- eslint-disable vue/no-v-html -->
<template>
  <div class="mt-5">
    <div v-if="props.field.errorsHtml" v-html="props.field.errorsHtml"></div>
    <label
      :for="props.field.id"
      class="block text-sm font-medium leading-6 text-gray-900"
    >
      {{ props.field.label }}
    </label>
    <div class="mt-2">
      <slot></slot>
    </div>
    <p v-if="props.field.helpText" class="mt-2 text-sm text-gray-500">
      <span v-html="props.field.helpText"></span>
    </p>
  </div>
</template>

<script lang="ts" setup>
import type { PropType } from 'vue';
import type { VueFieldInterface } from '@/js/types';

const props = defineProps({
  field: {
    type: Object as PropType<VueFieldInterface>,
    required: true,
  },
});
</script>
