import { defineConfig } from "vite";

// Vite kääntää JSX:n itse; tsconfig.json kertoo, että JSX on Reactin.
export default defineConfig({
  root: import.meta.dirname,
  base: "./",
  publicDir: "../yhteinen/julkinen",
  build: { outDir: "../dist/react", emptyOutDir: true },
});
