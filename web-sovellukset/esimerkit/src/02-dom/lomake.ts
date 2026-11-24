// @alku lomake
export type Hakuehdot = { vahintaan: number; varuste: string | null };

/** Lukee lomakkeen arvot FormDatasta. Selaimen oma validointi
 *  (required, min) on jo hyväksynyt arvot, kun submit laukeaa. */
export function lueHakuehdot(lomake: HTMLFormElement): Hakuehdot {
  const data = new FormData(lomake);
  const varuste = data.get("varuste");
  return {
    vahintaan: Number(data.get("vahintaan") ?? 1),
    varuste: typeof varuste === "string" && varuste !== "" ? varuste : null,
  };
}

export function kuunteleHakua(
  lomake: HTMLFormElement,
  kasittelija: (ehdot: Hakuehdot) => void,
): void {
  lomake.addEventListener("submit", (e) => {
    e.preventDefault();          // ei sivun latausta: sovellus hoitaa haun
    kasittelija(lueHakuehdot(lomake));
  });
}
// @loppu lomake
