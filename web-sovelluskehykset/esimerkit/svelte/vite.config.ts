import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

// Liitännäinen ajaa Svelten kääntäjän: .svelte-tiedostosta tulee
// JavaScript-moduuli, joka luo ja päivittää DOM:n suoraan.
export default defineConfig({
  root: import.meta.dirname,
  base: "./",
  publicDir: "../yhteinen/julkinen",
  plugins: [svelte()],
  build: { outDir: "../dist/svelte", emptyOutDir: true },
});
