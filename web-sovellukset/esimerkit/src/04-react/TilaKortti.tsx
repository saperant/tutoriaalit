import type { Tila } from "../tilat.ts";

// @alku kortti
type Props = {
  tila: Tila;
  onVaraa?: (id: string) => void;     // valinnainen: kortti voi olla
};                                    // pelkkä esitys

/** Esityskomponentti: saa kaiken propseina, ei omaa tilaa. */
export function TilaKortti({ tila, onVaraa }: Props) {
  return (
    <article aria-labelledby={`tila-${tila.id}`}>
      <h3 id={`tila-${tila.id}`}>{tila.nimi}</h3>
      <p>{tila.kerros}. krs, {tila.paikkoja} paikkaa</p>
      {tila.varusteet.length > 0 && (
        <p>Varusteet: {tila.varusteet.join(", ")}</p>
      )}
      {onVaraa && (
        <button type="button" onClick={() => onVaraa(tila.id)}>
          Varaa {tila.nimi}
        </button>
      )}
    </article>
  );
}
// @loppu kortti
