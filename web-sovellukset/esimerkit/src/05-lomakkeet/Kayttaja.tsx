import { createContext, type ReactNode, useContext } from "react";

// @alku konteksti
export type Kayttaja = { nimi: string; rooli: "kayttaja" | "yllapitaja" };

const KayttajaKonteksti = createContext<Kayttaja | null>(null);

export function KayttajaTarjoaja({ kayttaja, children }: {
  kayttaja: Kayttaja;
  children: ReactNode;
}) {
  return <KayttajaKonteksti value={kayttaja}>{children}</KayttajaKonteksti>;
}

/** Oma hook piilottaa kontekstin ja kertoo selvästi, jos tarjoaja
 *  puuttuu, sen sijaan että komponentti saisi hiljaa null-arvon. */
export function useKayttaja(): Kayttaja {
  const kayttaja = useContext(KayttajaKonteksti);
  if (!kayttaja) throw new Error("useKayttaja vaatii KayttajaTarjoajan");
  return kayttaja;
}
// @loppu konteksti

export function Tervehdys() {
  const { nimi, rooli } = useKayttaja();
  return <p>Kirjautunut: {nimi}{rooli === "yllapitaja" && " (ylläpito)"}</p>;
}
