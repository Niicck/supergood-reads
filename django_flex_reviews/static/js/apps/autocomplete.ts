import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp } from 'vue';
import ComboboxAutocomplete from '@/static/js/components/ComboboxAutocompleteDemo.vue';

const autocompleteApp = createApp(ComboboxAutocomplete);

autocompleteApp.mount('#autocomplete-vue-app');

export {};
