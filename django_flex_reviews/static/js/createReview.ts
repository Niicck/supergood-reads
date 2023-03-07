import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import { autocomplete } from '@algolia/autocomplete-js';
import '@algolia/autocomplete-theme-classic';

type MediaTypeContentItem = {
  label: string;
  id: string;
};

const parseJsonScriptFilter = (value: string): string => {
  /** Extract contents of "json_script" filter from a django template. */
  const element = document.getElementById(value);
  if (!element) {
    return '';
  }
  return JSON.parse(element.textContent || '');
};

const mountAutocomplete = (vueComponent: InstanceType<typeof formComponent>) => {
  autocomplete<MediaTypeContentItem>({
    container: '#media-type-autocomplete',
    openOnFocus: true,
    getSources({ setQuery }) {
      return [
        {
          sourceId: 'links',
          getItems({ query }) {
            return [
              { label: 'Star Wars', id: '1' },
              { label: 'Gone with the Wind', id: '2' },
              { label: 'Lord of the Rings', id: '3' },
              { label: 'Steel Magnolias', id: '4' },
              {
                label:
                  "Don't be a Menace to South Central while Drinking your Juice in the Hood",
                id: '5',
              },
            ].filter(({ label }) => label.toLowerCase().includes(query.toLowerCase()));
          },
          onSelect({ item }) {
            vueComponent.selectedMediaTypeObjectId = item.id;
            setQuery(item.label);
          },
          templates: {
            item({ item }) {
              return item.label;
            },
          },
        },
      ];
    },
  });
};

const formComponent = defineComponent({
  delimiters: ['[[', ']]'],
  data() {
    return {
      selectedStrategyId: parseJsonScriptFilter('initialSelectedStrategyId'),
      selectedMediaTypeContentType: parseJsonScriptFilter(
        'initialSelectedMediaTypeContentType',
      ),
      selectedMediaTypeObjectId: parseJsonScriptFilter(
        'initialSelectedMediaTypeObjectId',
      ),
    };
  },
  mounted() {
    mountAutocomplete(this);
  },
});

const formApp = createApp(formComponent);

formApp.mount('#review-form-vue-app');

export {};
