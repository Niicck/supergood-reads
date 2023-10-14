function safeParseInt(value: string | number | null, radix = 10): number | null {
  if (typeof value == 'number') {
    return value;
  }
  if (!value) {
    return null;
  }
  const parsed = parseInt(value, radix);
  return isNaN(parsed) ? null : parsed;
}

export { safeParseInt };
