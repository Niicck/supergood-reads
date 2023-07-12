<template>
  <tr class="align-text-top">
    <td
      class="w-full max-w-0 py-4 pr-3 text-sm font-medium text-gray-900 sm:w-auto sm:max-w-none sm:pl-0"
    >
      <!-- Title -->
      <div v-show="!editMode">
        {{ title }}
      </div>
      <div v-show="editMode" ref="titleFieldContainer">
        <slot
          name="title-field"
          :value="editedTitle"
          :on-changed="onTitleChanged"
          :field-errors="fieldErrors[props.titleFieldName]"
        ></slot>
      </div>
      <!-- On smaller screens, collapse data into first column -->
      <dl class="font-normal space-y-2 lg:hidden">
        <!-- Creator (small screens) -->
        <div v-show="!editMode">
          <dt class="sr-only">Author</dt>
          <dd class="mt-1 truncate text-gray-700">{{ creator }}</dd>
        </div>
        <div v-show="editMode">
          <slot
            name="creator-field"
            :value="editedCreator"
            :on-changed="onCreatorChanged"
            :field-errors="fieldErrors[props.creatorFieldName]"
          ></slot>
        </div>
        <!-- Year (small screens) -->
        <div class="sm:hidden">
          <div v-show="!editMode">
            <dt class="sr-only">Year</dt>
            <dd class="mt-1 truncate text-gray-500">{{ year }}</dd>
          </div>
          <div v-show="editMode">
            <slot
              name="year-field"
              :value="editedYear"
              :on-changed="onYearChanged"
              :field-errors="fieldErrors[props.yearFieldName]"
            ></slot>
          </div>
        </div>
      </dl>
    </td>
    <!-- Creator (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 lg:table-cell">
      <div v-show="!editMode">
        {{ creator }}
      </div>
      <div v-show="editMode">
        <slot
          name="creator-field"
          :value="editedCreator"
          :on-changed="onCreatorChanged"
          :field-errors="fieldErrors[props.creatorFieldName]"
        ></slot>
      </div>
    </td>
    <!-- Year (large screens) -->
    <td class="hidden px-3 py-4 text-sm text-gray-500 sm:table-cell">
      <div v-show="!editMode">
        {{ year }}
      </div>
      <div v-show="editMode">
        <slot
          name="year-field"
          :value="editedYear"
          :on-changed="onYearChanged"
          :field-errors="fieldErrors[props.yearFieldName]"
        ></slot>
      </div>
    </td>
    <!-- Media Type -->
    <td class="px-3 py-4 text-sm text-gray-500 sm:table-cell">{{ mediaType }}</td>
    <!-- Edit Button -->
    <td class="py-4 sm:pl-3 text-right text-sm font-medium sm:pr-0">
      <button
        type="button"
        class="text-indigo-600 hover:text-indigo-900 align-top w-12"
        @click="editMode = !editMode"
      >
        <span v-show="editMode"> Cancel </span>
        <span v-show="!editMode"> Edit </span>
        <span class="sr-only">, {{ title }}</span>
      </button>
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
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import DeleteModal from '@/static/js/components/DeleteModel.vue';

const props = defineProps({
  initialTitle: {
    type: String,
    default: null,
  },
  initialCreator: {
    type: String,
    default: null,
  },
  initialYear: {
    type: String,
    default: null,
  },
  titleFieldName: {
    type: String,
    default: null,
  },
  creatorFieldName: {
    type: String,
    default: null,
  },
  yearFieldName: {
    type: String,
    default: null,
  },
  mediaType: {
    type: String,
    default: null,
  },
  csrfToken: {
    type: String,
    default: '',
  },
  updateUrl: {
    type: String,
    default: '',
  },
});

const title = ref(props.initialTitle);
const creator = ref(props.initialCreator);
const year = ref(Number(props.initialYear));
const editedTitle = ref(props.initialTitle);
const editedCreator = ref(props.initialCreator);
const editedYear = ref(Number(props.initialYear));
const editMode = ref(false);
const showDeleteModal = ref(false);
const titleFieldContainer = ref<HTMLElement | null>(null);
const errorMessage = ref('');
const fieldErrors = ref<Partial<{ String: string[] }>>({});

const onTitleChanged = (event: Event) => {
  const target = event.target as HTMLInputElement;
  editedTitle.value = target.value;
};
const onCreatorChanged = (event: Event) => {
  const target = event.target as HTMLInputElement;
  editedCreator.value = target.value;
};
const onYearChanged = (event: Event) => {
  const target = event.target as HTMLInputElement;
  editedYear.value = Number(target.value);
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const onSubmit = () => {
  errorMessage.value = '';
  fieldErrors.value = {};
  return axios({
    method: 'post',
    url: props.updateUrl,
    data: {
      [props.titleFieldName]: editedTitle.value,
      [props.creatorFieldName]: editedCreator.value,
      [props.yearFieldName]: editedYear.value,
    },
    timeout: 5000,
    headers: {
      'Content-Type': 'multipart/form-data',
      'X-CSRFToken': props.csrfToken,
    },
  })
    .then((res) => {
      const data = res.data.data;
      title.value = editedTitle.value = data[props.titleFieldName];
      creator.value = editedCreator.value = data[props.creatorFieldName];
      year.value = editedYear.value = data[props.yearFieldName];
      editMode.value = false;
    })
    .catch((error) => {
      errorMessage.value = error.message;
      fieldErrors.value = error.response?.data?.errors;
    });
};

onMounted(() => {
  watch(editMode, (newValue) => {
    // Shift focus onto title-field once we enter editMode.
    if (newValue == true) {
      nextTick(() => {
        const titleFieldInput = titleFieldContainer?.value?.querySelector('input');
        titleFieldInput?.focus();
      });
    }
  });
});
</script>
