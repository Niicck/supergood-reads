import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, Component } from 'vue';

const parseJsonScriptFilter = (value: string): string => {
  /** Extract contents of "json_script" filter from a django template. */
  const element = document.getElementById(value);
  if (!element) {
    return '';
  }
  return JSON.parse(element.textContent || '');
};

const formComponent: Component = {
  delimiters: ['[[', ']]'],
  data() {
    return {
      selectedStrategyId: parseJsonScriptFilter('initialSelectedStrategyId'),
    };
  },
};

const formApp = createApp(formComponent);

formApp.mount('#review-form-vue-app');

export {};
