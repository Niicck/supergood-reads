<template>
  <!-- Notification panel, dynamically insert this into the live region when it needs to be displayed -->
  <transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
    enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
    leave-active-class="transition ease-in duration-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5"
    >
      <div class="p-4 flex items-start">
        <div v-if="props.levelTag == 'error'" class="flex items-start flex-1">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-6 w-6 text-red-400" aria-hidden="true" />
          </div>
          <div class="ml-3 pt-0.5 flex-1">
            <p class="capitalize text-sm font-medium text-gray-900">
              {{ props.levelTag }}
            </p>
            <p class="mt-1 text-sm text-gray-500">{{ props.message }}</p>
          </div>
        </div>
        <div v-else-if="props.levelTag == 'success'" class="flex items-start flex-1">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-6 w-6 text-green-400" aria-hidden="true" />
          </div>
          <div class="ml-3 pt-0.5 flex-1">
            <p class="capitalize text-sm font-medium text-gray-900">
              {{ props.levelTag }}
            </p>
            <p class="mt-1 text-sm text-gray-500">{{ props.message }}</p>
          </div>
        </div>
        <div v-else class="flex items-start flex-1">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon
              class="h-6 w-6 text-yellow-400"
              aria-hidden="true"
            />
          </div>
          <div class="ml-3 pt-0.5 flex-1">
            <p class="capitalize text-sm font-medium text-gray-900">
              {{ props.levelTag }}
            </p>
            <p class="mt-1 text-sm text-gray-500">{{ props.message }}</p>
          </div>
        </div>
        <div class="ml-4 flex flex-shrink-0">
          <button
            type="button"
            class="inline-flex rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            @click="show = false"
          >
            <span class="sr-only">Close</span>
            <XMarkIcon class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import type { PropType } from 'vue';
import { CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import type { MessageLevelTag } from '@/js/stores/messages';
import { XMarkIcon } from '@heroicons/vue/20/solid';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  /**
   * The text content of the django message.
   * https://docs.djangoproject.com/en/4.1/ref/contrib/messages/#the-message-class
   */
  message: {
    type: String,
    default: null,
  },
  /**
   * The string representation of the django message's level.
   * https://docs.djangoproject.com/en/4.1/ref/contrib/messages/#the-message-class
   */
  levelTag: {
    type: String as PropType<MessageLevelTag>,
    default: '',
  },
});

const show = ref(true);
</script>
