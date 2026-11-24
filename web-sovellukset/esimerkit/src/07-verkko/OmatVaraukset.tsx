import { useState } from "react";

export type Varaus = { id: string; tila: string; aika: string };

// @alku optimistinen
/** Peruutus näkyy heti (optimistinen päivitys). Jos palvelin hylkää
 *  peruutuksen, varaus palautetaan ja virhe kerrotaan. */
export function OmatVaraukset({ alku, peru }: {
  alku: readonly Varaus[];
  peru: (id: string) => Promise<void>;
}) {
  const [varaukset, setVaraukset] = useState(alku);
  const [virhe, setVirhe] = useState<string | null>(null);

  async function peruVaraus(varaus: Varaus) {
    setVirhe(null);
    setVaraukset((nyt) => nyt.filter((v) => v.id !== varaus.id));
    try {
      await peru(varaus.id);
    } catch {
      // Palautetaan funktiona nykyiseen tilaan: välissä on voinut
      // tapahtua muita muutoksia, joita ei saa kumota.
      setVaraukset((nyt) => [...nyt, varaus]
        .sort((a, b) => a.aika.localeCompare(b.aika)));
      setVirhe(`Varauksen ${varaus.tila} ${varaus.aika} peruutus ` +
               "epäonnistui.");
    }
  }

  return (
    <section aria-labelledby="omat">
      <h2 id="omat">Omat varaukset</h2>
      <ul>
        {varaukset.map((v) => (
          <li key={v.id}>
            {v.tila} {v.aika}{" "}
            <button type="button" onClick={() => void peruVaraus(v)}>
              Peru {v.tila} {v.aika}
            </button>
          </li>
        ))}
      </ul>
      <p role="alert">{virhe}</p>
    </section>
  );
}
// @loppu optimistinen
