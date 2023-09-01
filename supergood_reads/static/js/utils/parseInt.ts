function safeParseInt(value: any, radix = 10): number | null {
  const parsed = parseInt(value, radix);
  return isNaN(parsed) ? null : parsed;
}

export { safeParseInt };
