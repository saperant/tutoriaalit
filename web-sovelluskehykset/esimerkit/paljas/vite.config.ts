import { defineConfig } from "vite";

export default defineConfig({
  root: import.meta.dirname,
  base: "./",
  publicDir: "../yhteinen/julkinen",
  build: { outDir: "../dist/paljas", emptyOutDir: true },
});
