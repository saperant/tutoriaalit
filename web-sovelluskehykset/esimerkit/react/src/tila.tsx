// Jaettu tila: reducer ja konteksti. Tila on yksi muuttumaton arvo,
// jota muutetaan vain lähettämällä toiminto (dispatch).
import {
  createContext, useCallback, useContext, useEffect, useReducer,
  type Dispatch, type ReactNode,
} from "react";
import * as logiikka from "../../yhteinen/logiikka.ts";
import type { Kiire, Lataus, Tehtava } from "../../yhteinen/logiikka.ts";

// @alku reducer
interface Tila { lataus: Lataus; tehtavat: readonly Tehtava[] }

type Toiminto =
  | { tyyppi: "ladattu"; tehtavat: Tehtava[] }
  | { tyyppi: "lataus"; lataus: Lataus }
  | { tyyppi: "lisaa"; nimi: string; kiire: Kiire }
  | { tyyppi: "vaihda" | "poista"; id: number }
  | { tyyppi: "poistaValmiit" };

function reducer(tila: Tila, t: Toiminto): Tila {
  const uusi = (tehtavat: Tehtava[]): Tila => ({ ...tila, tehtavat });
  switch (t.tyyppi) {
    case "ladattu": return { lataus: "valmis", tehtavat: t.tehtavat };
    case "lataus": return { ...tila, lataus: t.lataus };
    case "lisaa": return uusi(logiikka.lisaa(tila.tehtavat, t.nimi, t.kiire));
    case "vaihda": return uusi(logiikka.vaihda(tila.tehtavat, t.id));
    case "poista": return uusi(logiikka.poista(tila.tehtavat, t.id));
    case "poistaValmiit": return uusi(logiikka.poistaValmiit(tila.tehtavat));
  }
}
// @loppu reducer

// @alku konteksti
interface Arvo { tila: Tila; laheta: Dispatch<Toiminto>; lataa: () => void }
const Konteksti = createContext<Arvo | null>(null);

export function TehtavatTarjoaja({ children }: { children: ReactNode }) {
  const [tila, laheta] = useReducer(reducer,
    { lataus: "ladataan", tehtavat: [] });

  const lataa = useCallback(() => {
    laheta({ tyyppi: "lataus", lataus: "ladataan" });
    logiikka.haeTehtavat(localStorage).then(
      (tehtavat) => laheta({ tyyppi: "ladattu", tehtavat }),
      () => laheta({ tyyppi: "lataus", lataus: "virhe" }),
    );
  }, []);
  useEffect(lataa, [lataa]);

  // Sivuvaikutukset: tila on totuus, selaimen muisti ja otsikko seuraavat.
  useEffect(() => {
    if (tila.lataus !== "valmis") return;
    logiikka.tallenna(localStorage, tila.tehtavat);
    document.title = logiikka.otsikko(tila.tehtavat);
  }, [tila]);

  return <Konteksti value={{ tila, laheta, lataa }}>{children}</Konteksti>;
}

export function useTehtavat(): Arvo {
  const arvo = useContext(Konteksti);
  if (arvo === null) throw new Error("TehtavatTarjoaja puuttuu");
  return arvo;
}
// @loppu konteksti
