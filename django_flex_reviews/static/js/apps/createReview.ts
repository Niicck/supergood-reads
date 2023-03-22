import 'vite/modulepreload-polyfill'; // required for vite entrypoints
import { createApp, defineComponent } from 'vue';
import { createPinia } from 'pinia';
import RadioCards from '@/static/js/components/RadioCards.vue';
import { useCreateReviewStore } from '@/static/js/stores';
import ComboboxAutocomplete from '@/static/js/components/ComboboxAutocomplete.vue';

const pinia = createPinia();

const RootComponent = defineComponent({
  delimiters: ['[[', ']]'],
  components: {
    'radio-cards': RadioCards,
    'autocomplete': ComboboxAutocomplete,
  },
  setup() {
    const store = useCreateReviewStore();
    window.store = store;
    return { store };
  },
  mounted() {
    const toggleRequiredFieldsOnForms = (
      formContainerRefPrefix: string,
      isFormRequired: boolean,
      selectedContentTypeId: string,
    ) => {
      /**
       * If we're creating a new MediaType Instance (Book/Film) with our Review, then
       * the fields for generating that MediaType Instance (title/author/year/etc.)
       * should be required on submit. However, if we're just selecting an existing
       * MediaType instance, then those fields for creating a new instance should not
       * required.
       *
       * This watcher will assign the correct values for "required" on those form
       * fields based on changes in state.
       *
       * This watcher is defined within mounted() because template refs (this.$refs)
       * do not exist until the app is mounted. We select the forms we want to modify
       * based on dynamic ref= attributes within the django template.
       *
       * The watcher is invoked immediately {immediate: true} in order to set correct
       * "required" field values based on the initial values of
       * createNewMediaTypeObject and selectedMediaTypeContentType.
       *
       * @param formContainerRefPrefix: Narrow down the template $refs to just the
       *  form containers that would be impacted by "isFormRequired" and
       *  "selectedContentTypeId".
       * @param isFormRequired: Should the fields within this form be marked as
       *  "required"?
       * @param selectedContentTypeId: The id of the form that would be required.
       */
      const requiredFormContainerRefId = formContainerRefPrefix + selectedContentTypeId;
      const requiredFormContainer: HTMLElement | undefined = this.$refs[
        requiredFormContainerRefId
      ] as HTMLElement | undefined;

      const allFormContainerRefEntries: Array<[string, HTMLElement]> = Object.entries(
        this.$refs,
      ) as Array<[string, HTMLElement]>;
      const allFormContainers: Array<HTMLElement> = allFormContainerRefEntries
        .filter((ref) => ref[0].startsWith(formContainerRefPrefix))
        .map((ref) => ref[1]);

      let unrequiredFormContainers: Array<HTMLElement>;

      // If user chooses to createNewMediaTypeObject rather than choosing an existing
      // one, then mark the form fields for that media_type_form as required.
      if (isFormRequired && requiredFormContainer) {
        requiredFormContainer
          .querySelectorAll('input, select, textarea')
          .forEach((input) => {
            input.setAttribute('required', '');
          });
        unrequiredFormContainers = allFormContainers.filter(
          (container) => container !== requiredFormContainer,
        );
      } else {
        unrequiredFormContainers = allFormContainers;
      }

      // Mark form fields for unneeded forms as not required.
      unrequiredFormContainers.forEach((container) => {
        const formInputs = container.querySelectorAll('input, select, textarea');
        formInputs.forEach((input) => {
          input.removeAttribute('required');
        });
      });
    };

    // Handle "required" attribute toggling for new MediaType Instance forms.
    this.$watch(
      () => [
        this.store.createNewMediaTypeObject,
        this.store.selectedMediaTypeContentType,
      ],
      ([createNewMediaTypeObject, selectedMediaTypeContentType]) => {
        toggleRequiredFieldsOnForms(
          'media_type_form_',
          createNewMediaTypeObject as boolean,
          selectedMediaTypeContentType as string,
        );
      },
      { immediate: true },
    );

    // Handle "required" attribute toggling for new Strategy Instance forms.
    this.$watch(
      () => this.store.selectedStrategyId,
      (selectedStrategyId) => {
        toggleRequiredFieldsOnForms(
          'strategy_form_',
          true,
          selectedStrategyId as string,
        );
      },
      { immediate: true },
    );
  },
});

const app = createApp(RootComponent);
app.use(pinia);
app.mount('#review-form-vue-app');

export {};
