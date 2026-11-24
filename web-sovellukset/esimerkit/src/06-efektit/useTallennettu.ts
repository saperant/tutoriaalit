import { useCallback, useSyncExternalStore } from "react";

// @alku tallennettu
/** Arvo selaimen localStoragessa. Tallennettu data on epäluotettavaa
 *  (vanha versio, käsin muokattu), joten se jäsennetään lukiessa. */
export function useTallennettu<T>(
  avain: string,
  oletus: T,
  jasenna: (raaka: unknown) => T | null,
): [T, (uusi: T) => void] {
  // Tilaus: muiden välilehtien muutokset tulevat storage-tapahtumina,
  // saman välilehden muutokset omana tapahtumanaan.
  const tilaa = useCallback((ilmoita: () => void) => {
    window.addEventListener("storage", ilmoita);
    window.addEventListener("tallennettu", ilmoita);
    return () => {
      window.removeEventListener("storage", ilmoita);
      window.removeEventListener("tallennettu", ilmoita);
    };
  }, []);
  // Tilannekuvan on oltava vakaa: palautetaan merkkijono, ei uutta oliota.
  const raaka = useSyncExternalStore(tilaa,
    () => localStorage.getItem(avain), () => null);

  const arvo = lue(raaka, jasenna) ?? oletus;
  const aseta = useCallback((uusi: T) => {
    localStorage.setItem(avain, JSON.stringify(uusi));
    window.dispatchEvent(new Event("tallennettu"));
  }, [avain]);
  return [arvo, aseta];
}

function lue<T>(raaka: string | null,
                jasenna: (x: unknown) => T | null): T | null {
  if (raaka === null) return null;
  try { return jasenna(JSON.parse(raaka)); } catch { return null; }
}
// @loppu tallennettu
