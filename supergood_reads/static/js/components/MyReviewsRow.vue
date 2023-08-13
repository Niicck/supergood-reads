<template>
  <tr class="align-text-top">
    <td
      class="w-full max-w-0 py-4 pr-3 text-sm font-medium text-gray-900 sm:w-auto sm:max-w-none sm:pl-0"
    >
      <!-- Title -->
      <div>
        <p>{{ title }}</p>
        <p class="text-gray-700">({{ mediaType }})</p>
      </div>
      <!-- On smaller screens, collapse data into first column -->
      <dl class="font-normal space-y-2 lg:hidden">
        <!-- CompletedAt (small screens) -->
        <div v-show="!editMode">
          <dt class="sr-only">Completed at</dt>
          <dd class="mt-1 truncate text-gray-700">{{ completedAt }}</dd>
        </div>
        <div v-show="editMode" ref="firstFieldContainer">
          <slot name="date-picker"></slot>
        </div>
        <!-- Rating (small screens) -->
        <div class="sm:hidden">
          <div v-show="!editMode">
            <dt class="sr-only">Rating</dt>
            <dd class="mt-1 truncate text-gray-500">{{ rating }}</dd>
          </div>
          <div v-show="editMode">
            <slot name="text-field"></slot>
          </div>
        </div>
      </dl>
    </td>
    <!-- CompletedAt (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 lg:table-cell">
      <div v-show="!editMode">
        {{ completedAt }}
      </div>
      <div v-show="editMode">
        <slot name="date-picker"></slot>
      </div>
    </td>
    <!-- Rating (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">
      <div v-show="!editMode">
        {{ rating }}
      </div>
      <div v-show="editMode">
        <slot name="text-field"></slot>
      </div>
    </td>
    <!-- Edit Button -->
    <td class="py-4 sm:pl-3 text-right text-sm font-medium sm:pr-0">
      <a
        type="button"
        class="text-indigo-600 hover:text-indigo-900 align-top w-12"
        :href="props.updateUrl"
      >
        Edit <span class="sr-only">, Review of {{ title }}</span>
      </a>
    </td>
  </tr>

  <tr class="border-none">
    <td class="pb-4">
      <div v-show="!editMode">
        {{ text }}
      </div>
      <div v-show="editMode">
        <slot name="text-field"></slot>
      </div>
    </td>
  </tr>

  <tr v-show="editMode" class="border-none">
    <p v-if="errorMessage" role="alert" class="mb-2 text-sm text-red-600">
      {{ errorMessage }}
    </p>
    <td class="flex justify-start pb-5 space-x-3">
      <!-- Submit Button -->
      <button
        class="cursor-pointer inline-flex justify-center rounded-md bg-indigo-600 py-2 px-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        @click="onSubmit"
      >
        Submit
      </button>
      <!-- Delete Button -->
      <button
        class="cursor-pointer inline-flex justify-center rounded-md bg-red-600 py-2 px-3 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
        @click="showDeleteModal = true"
      >
        Delete
      </button>
    </td>
  </tr>
  <DeleteModal
    v-if="showDeleteModal"
    :close-delete-modal="closeDeleteModal"
    :title="title"
  >
    <template #delete-form>
      <slot name="delete-form"></slot>
    </template>
  </DeleteModal>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue';
import axios from 'axios';
import type { MyReviewRowInitialData } from '@/static/js/types';
import { parseJsonScript } from '@/static/js/utils/parseJsonScript';
import DeleteModal from '@/static/js/components/DeleteModal.vue';

const props = defineProps({
  jsonScriptId: {
    type: String,
    required: true,
  },
  csrfToken: {
    type: String,
    required: true,
  },
  updateUrl: {
    type: String,
    required: true,
  },
});

const initialData = ref<MyReviewRowInitialData>({
  initialTitle: '',
  initialMediaType: '',
  initialCompletedAt: '',
  initialRating: '',
  initialText: '',
});

const title = computed(() => initialData.value.initialTitle);
const mediaType = computed(() => initialData.value.initialMediaType);
const completedAt = computed(() => initialData.value.initialCompletedAt);
const rating = computed(() => initialData.value.initialRating);
const text = computed(() => initialData.value.initialText);

const editedText = ref('');
const editMode = ref(false);
const showDeleteModal = ref(false);
const firstFieldContainer = ref<HTMLElement | null>(null);
const errorMessage = ref('');
const fieldErrors = ref<Partial<{ String: string[] }>>({});

/**
 * Retrieve the fieldData value from the json data embedded into a <script> tag by the
 * json_script django filter.
 */
onMounted(() => {
  initialData.value = parseJsonScript(props.jsonScriptId) as MyReviewRowInitialData;
  editedText.value = initialData.value.initialText;
});

const onTextChanged = (event: Event) => {
  const target = event.target as HTMLInputElement;
  editedText.value = target.value;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

// const onSubmit = () => {
//   errorMessage.value = '';
//   fieldErrors.value = {};
//   return axios({
//     method: 'post',
//     url: props.updateUrl,
//     data: {
//       [props.titleFieldName]: editedTitle.value,
//       [props.creatorFieldName]: editedCreator.value,
//       [props.yearFieldName]: editedYear.value,
//     },
//     timeout: 5000,
//     headers: {
//       'Content-Type': 'multipart/form-data',
//       'X-CSRFToken': props.csrfToken,
//     },
//   })
//     .then((res) => {
//       const data = res.data.data;
//       title.value = editedTitle.value = data[props.titleFieldName];
//       creator.value = editedCreator.value = data[props.creatorFieldName];
//       year.value = editedYear.value = data[props.yearFieldName];
//       editMode.value = false;
//     })
//     .catch((error) => {
//       errorMessage.value = error.message;
//       fieldErrors.value = error.response?.data?.errors;
//     });
// };

onMounted(() => {
  watch(editMode, (newValue) => {
    // Shift input focus onto thhe first field once we enter editMode.
    if (newValue == true) {
      nextTick(() => {
        const titleFieldInput = firstFieldContainer?.value?.querySelector('input');
        titleFieldInput?.focus();
      });
    }
  });
});
</script>
