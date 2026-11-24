import { useState } from "react";
import type { Tila } from "../tilat.ts";
import { TilaLista } from "./TilaLista.tsx";

// @alku haku
/** Säiliökomponentti: omistaa hakutilan ja johtaa siitä näkymän. */
export function TilaHaku({ tilat, onVaraa }: {
  tilat: readonly Tila[];
  onVaraa: (id: string) => void;
}) {
  const [haku, setHaku] = useState("");
  const [vahintaan, setVahintaan] = useState(1);

  // Johdettu arvo lasketaan renderöinnissä: ei omaa tilaa, ei efektiä.
  const osumat = tilat.filter((t) =>
    t.paikkoja >= vahintaan &&
    t.nimi.toLowerCase().includes(haku.trim().toLowerCase()));

  return (
    <section>
      <label>
        Hae nimellä{" "}
        <input type="search" value={haku}
               onChange={(e) => setHaku(e.target.value)} />
      </label>
      <label>
        Paikkoja vähintään{" "}
        <input type="number" min={1} value={vahintaan}
               onChange={(e) => setVahintaan(Number(e.target.value))} />
      </label>
      <p aria-live="polite">{osumat.length} / {tilat.length} tilaa</p>
      <TilaLista tilat={osumat} onVaraa={onVaraa} />
    </section>
  );
}
// @loppu haku
