/**
 * The type of the output of the custom field_to_dict django filter.
 */
type FieldData = {
  html_name: string;
  label: string;
  id_for_label: string;
  choices: Array<Array<string | number | boolean>>;
};

type NavBarLink = {
  href: string;
  name: string;
  current: boolean;
};

type MyReviewRowInitialData = {
  initialTitle: string;
  initialMediaType: string;
  initialCompletedAt: string;
  initialRating: string;
  initialText: string;
};

export type { FieldData, NavBarLink, MyReviewRowInitialData };
