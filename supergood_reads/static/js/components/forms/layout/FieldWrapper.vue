/* eslint vue/no-v-html: "off" */
<template>
  <div class="mt-5">
    <div v-html="fieldData.errors_html"></div>
    <label
      :for="fieldData.id_for_label"
      class="block text-sm font-medium leading-6 text-gray-900"
    >
      {{ fieldData.label }}
    </label>
    <div class="mt-2">
      <slot name="field" :field-data="fieldData"></slot>
    </div>
    <p v-if="fieldData.help_text" class="mt-2 text-sm text-gray-500">
      <span v-html="fieldData.help_text"></span>
    </p>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import type { FieldData } from '@/js/types';
import { parseJsonScript } from '@/js/utils/parseJsonScript';

const props = defineProps({
  /**
   * The id attribute of the <script> element where the django field's metadata was
   * was stored as an output of the django json_script filter.
   */
  fieldDataJsonScriptId: {
    type: String,
    default: null,
  },
});

const fieldData = ref<FieldData>({
  errors_html: '',
  html_name: '',
  label: '',
  id_for_label: '',
  choices: [],
});

/**
 * Retrieve the fieldData value from the json data embedded into a <script> tag by the
 * json_script django filter.
 */
onMounted(() => {
  fieldData.value = parseJsonScript(props.fieldDataJsonScriptId) as FieldData;
});
</script>
