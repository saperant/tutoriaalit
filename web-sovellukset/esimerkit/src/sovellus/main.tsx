import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { luoAsiakas } from "../07-verkko/asiakas.ts";
import { Sovellus } from "./Sovellus.tsx";

// @alku main
const juuri = document.getElementById("sovellus");
if (!juuri) throw new Error("index.html: #sovellus puuttuu");

// StrictMode ajaa kehitystilassa efektit kahdesti ja paljastaa näin
// puuttuvat siivoukset. Tuotantokäännöksessä se ei tee mitään.
createRoot(juuri).render(
  <StrictMode>
    <Sovellus api={luoAsiakas("")}
              tanaan={new Date().toISOString().slice(0, 10)} />
  </StrictMode>,
);
// @loppu main
