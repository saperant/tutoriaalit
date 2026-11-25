import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../../yhteinen/tyyli.css";
import { Sovellus } from "./Sovellus.tsx";
import { TehtavatTarjoaja } from "./tila.tsx";

createRoot(document.getElementById("juuri")!).render(
  <StrictMode>
    <TehtavatTarjoaja>
      <Sovellus />
    </TehtavatTarjoaja>
  </StrictMode>,
);
