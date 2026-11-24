import { useEffect, useState } from "react";

// @alku viivastetty
/** Palauttaa arvon vasta, kun se on pysynyt samana `ms` millisekuntia
 *  (debounce). Hakukenttä ei näin lähetä pyyntöä joka näppäilystä. */
export function useViivastetty<T>(arvo: T, ms: number): T {
  const [viivastetty, setViivastetty] = useState(arvo);
  useEffect(() => {
    const ajastin = setTimeout(() => setViivastetty(arvo), ms);
    return () => clearTimeout(ajastin);    // siivous: uusi arvo peruu vanhan
  }, [arvo, ms]);
  return viivastetty;
}
// @loppu viivastetty
