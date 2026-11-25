import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

// Liitännäinen kääntää .vue-tiedostot: mallipohjasta tulee
// renderöintifunktio jo käännösvaiheessa.
export default defineConfig({
  root: import.meta.dirname,
  base: "./",
  publicDir: "../yhteinen/julkinen",
  plugins: [vue()],
  build: { outDir: "../dist/vue", emptyOutDir: true },
});
