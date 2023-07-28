const parseJsonScriptFilter = (value: string): string | object | boolean => {
  /** Extract contents of "json_script" filter from a django template. */
  if (!value) {
    return '';
  }
  const element = document.getElementById(value);
  if (!element) {
    return '';
  }
  return JSON.parse(element.textContent || '');
};

export { parseJsonScriptFilter };
