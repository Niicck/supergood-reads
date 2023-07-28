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
              { label: 'The Seventh Seal', id: '1' },
              { label: 'Rebel without a Cause', id: '2' },
              { label: 'Seven Samurai', id: '3' },
              { label: 'Before Sunset', id: '4' },
              {
                label:
                  'Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb',
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
