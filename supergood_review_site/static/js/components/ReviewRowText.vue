<template>
  <tr class="border-none review-row-vue-app">
    <td class="pb-4 pl-4 min-w-full" colspan="2">
      <div>
        <span v-if="expanded || !hasMore">
          {{ text }}
        </span>
        <span v-else> {{ truncatedText }}... </span>
        <span v-if="hasMore">
          <button
            type="button"
            class="rounded bg-white px-2 py-1 ml-2 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            @click="expanded = !expanded"
          >
            {{ expanded ? 'Show less' : 'Show more' }}
          </button>
        </span>
      </div>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
});

const expanded = ref(false);

const characterCutoff = 100;
const truncatedText = props.text.slice(0, characterCutoff);
const hasMore = truncatedText.length < props.text.length;
</script>
