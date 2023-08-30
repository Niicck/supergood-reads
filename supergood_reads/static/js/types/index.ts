export interface VueFieldInterface {
  errorsHtml?: string;
  name: string;
  label: string;
  id: string;
  helpText?: string;
  initialValue?: string | number;
  choices?: Array<Array<string | number>>;
  disabled?: boolean;
}

export type NavBarLink = {
  href: string;
  name: string;
  current: boolean;
};

export type MyReviewRowInitialData = {
  initialTitle: string;
  initialMediaType: string;
  initialCompletedAt: string;
  initialRating: string;
  initialText: string;
};

export type FilterOption = {
  value: string;
  label: string;
  checked: boolean;
};

export type Filter = {
  id: string;
  name: string;
  options: Array<FilterOption>;
  clear: boolean;
};

export type MediaSearchResult = {
  id: string;
  title: string;
  year: number;
  creator: string;
  genres: string[];
  icon: string;
  UpdateUrl: string;
};
