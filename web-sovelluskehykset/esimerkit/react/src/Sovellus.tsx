import { useState } from "react";
import { suodata, type Suodatin } from "../../yhteinen/logiikka.ts";
import { Lisayslomake } from "./Lisayslomake.tsx";
import { SuodatinValinta } from "./SuodatinValinta.tsx";
import { TehtavaRivi } from "./TehtavaRivi.tsx";
import { useTehtavat } from "./tila.tsx";
import { Yhteenveto } from "./Yhteenveto.tsx";

// @alku sovellus
export function Sovellus() {
  const { tila, laheta, lataa } = useTehtavat();
  // Suodatin on vain tämän näkymän asia, joten se on paikallista tilaa.
  const [suodatin, setSuodatin] = useState<Suodatin>("kaikki");
  // Johdettu tieto lasketaan renderöinnissä, sitä ei tallenneta tilaan.
  const nakyvat = suodata(tila.tehtavat, suodatin);

  return (
    <>
      <header className="ylapalkki">
        <h1>Tehtävät</h1>
        <Yhteenveto />
      </header>
      <main>
        <Lisayslomake />
        <SuodatinValinta arvo={suodatin} onMuutos={setSuodatin} />
        {tila.lataus === "ladataan" &&
          <p className="tila">Ladataan tehtäviä…</p>}
        {tila.lataus === "virhe" && <>
          <p className="virhe" role="alert">
            Tehtävien lataus epäonnistui.
          </p>
          <button type="button" onClick={lataa}>Yritä uudelleen</button>
        </>}
        {tila.lataus === "valmis" && <>
          {nakyvat.length === 0
            ? <p className="tila">Ei näytettäviä tehtäviä.</p>
            : <ul className="tehtavat" aria-label="Tehtävät">
                {nakyvat.map((t) =>
                  <TehtavaRivi key={t.id} tehtava={t}
                    onVaihda={() => laheta({ tyyppi: "vaihda", id: t.id })}
                    onPoista={() => laheta({ tyyppi: "poista", id: t.id })}
                  />)}
              </ul>}
          <button type="button"
                  disabled={!tila.tehtavat.some((t) => t.valmis)}
                  onClick={() => laheta({ tyyppi: "poistaValmiit" })}>
            Poista valmiit
          </button>
        </>}
      </main>
    </>
  );
}
// @loppu sovellus
