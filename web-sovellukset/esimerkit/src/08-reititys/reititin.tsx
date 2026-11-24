import { type MouseEvent, type ReactNode, useSyncExternalStore } from "react";

// Pieni reititin selaimen History API:n päälle. Tuotannossa käytetään
// valmista (React Router, TanStack Router), mutta periaate on sama.

// @alku sijainti
const MUUTOS = "sijainti-muuttui";

function tilaa(ilmoita: () => void) {
  window.addEventListener("popstate", ilmoita);   // takaisin/eteenpäin
  window.addEventListener(MUUTOS, ilmoita);       // oma siirry()
  return () => {
    window.removeEventListener("popstate", ilmoita);
    window.removeEventListener(MUUTOS, ilmoita);
  };
}

/** URL on sovelluksen tilaa: polku ja hakuparametrit. */
export function useSijainti(): URL {
  const osoite = useSyncExternalStore(tilaa, () => location.href);
  return new URL(osoite);
}

export function siirry(osoite: string, { korvaa = false } = {}): void {
  if (korvaa) history.replaceState(null, "", osoite);
  else history.pushState(null, "", osoite);
  window.dispatchEvent(new Event(MUUTOS));
}
// @loppu sijainti

// @alku linkki
/** Tavallinen linkki, joka siirtyy ilman sivun latausta. Ctrl-, Cmd- ja
 *  vaihtonäppäimellä selain hoitaa linkin itse (uusi välilehti). */
export function Linkki({ to, children }: {
  to: string;
  children: ReactNode;
}) {
  function onClick(e: MouseEvent<HTMLAnchorElement>) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey ||
        e.altKey) return;
    e.preventDefault();
    siirry(to);
  }
  return <a href={to} onClick={onClick}>{children}</a>;
}
// @loppu linkki

// @alku sovita
/** Sovittaa polun malliin, esim. "/tilat/:id". */
export function sovita(malli: string, polku: string)
  : Record<string, string> | null {
  const osat = malli.split("/");
  const arvot = polku.split("/");
  if (osat.length !== arvot.length) return null;
  const parametrit: Record<string, string> = {};
  for (const [i, osa] of osat.entries()) {
    const arvo = arvot[i] ?? "";
    if (osa.startsWith(":")) parametrit[osa.slice(1)] =
      decodeURIComponent(arvo);
    else if (osa !== arvo) return null;
  }
  return parametrit;
}
// @loppu sovita

// @alku hakuparametri
/** Hakuparametri tilana: suodatin säilyy kirjanmerkissä, jaetussa
 *  linkissä ja sivun päivityksessä. Kirjoittaminen korvaa historian
 *  kohdan, jotta jokainen näppäily ei ole oma Takaisin-askel. */
export function useHakuparametri(
  nimi: string,
): [string, (arvo: string) => void] {
  const sijainti = useSijainti();
  const arvo = sijainti.searchParams.get(nimi) ?? "";
  const aseta = (uusi: string) => {
    const url = new URL(location.href);
    if (uusi) url.searchParams.set(nimi, uusi);
    else url.searchParams.delete(nimi);
    siirry(url.pathname + url.search, { korvaa: true });
  };
  return [arvo, aseta];
}
// @loppu hakuparametri
