import { defineComponent } from 'vue';
import { autocomplete } from '@algolia/autocomplete-js';
import '@algolia/autocomplete-theme-classic';

type MediaTypeContentItem = {
  label: string;
  id: string;
};

const mountAutocomplete = () => {
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
            // TODO: emit state change
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

const AlgoliaAutocomplete = defineComponent({
  mounted() {
    mountAutocomplete();
  },
});

export { AlgoliaAutocomplete };
