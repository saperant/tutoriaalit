import { useEffect, useState } from "react";

// @alku haku
export type Haku<T> =
  | { tila: "ladataan" }
  | { tila: "valmis"; data: T }
  | { tila: "virhe"; virhe: Error };

/** Hakee datan, kun avain muuttuu. Edellinen pyyntö perutaan, joten
 *  hitaasti valmistuva vanha vastaus ei voi korvata uutta (kilpatilanne). */
export function useHaku<T>(
  avain: string,
  hae: (signal: AbortSignal) => Promise<T>,
): Haku<T> & { yritaUudelleen: () => void } {
  const [tulos, setTulos] = useState<{ avain: string; haku: Haku<T> }>(
    { avain, haku: { tila: "ladataan" } });
  const [kierros, setKierros] = useState(0);

  useEffect(() => {
    const peruutus = new AbortController();
    hae(peruutus.signal).then(
      (data) => {
        if (peruutus.signal.aborted) return;     // vanha vastaus: hylätään
        setTulos({ avain, haku: { tila: "valmis", data } });
      },
      (virhe: unknown) => {
        if (peruutus.signal.aborted) return;     // peruttu: ei näytetä
        setTulos({ avain, haku: { tila: "virhe", virhe:
          virhe instanceof Error ? virhe : new Error(String(virhe)) } });
      });
    return () => peruutus.abort();
  }, [avain, kierros]);   // hae puuttuu tarkoituksella: avain ratkaisee

  // Avaimen vaihtuessa vanhaa dataa ei näytetä uuden avaimen datana.
  const haku: Haku<T> = tulos.avain === avain
    ? tulos.haku : { tila: "ladataan" };
  return { ...haku, yritaUudelleen: () => setKierros((k) => k + 1) };
}
// @loppu haku
