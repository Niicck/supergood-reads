/**
 * Allow import of .vue files into .ts files.
 * Fixes:
 * error TS2307: Cannot find module '@/static/vue/Autocomplete.vue' or its corresponding type declarations.
 **/
declare module '*.vue';
