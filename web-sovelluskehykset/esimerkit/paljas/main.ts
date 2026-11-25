// Toteutus ilman kehystä: tila on tavallisissa muuttujissa, ja jokaisen
// muutoksen jälkeen DOM saatetaan käsin vastaamaan tilaa. Tämä on se
// työ, jonka kehykset tekevät puolestasi.
import "../yhteinen/tyyli.css";
import * as logiikka from "../yhteinen/logiikka.ts";
import type { Kiire, Lataus, Suodatin, Tehtava }
  from "../yhteinen/logiikka.ts";

// @alku tila
let tehtavat: readonly Tehtava[] = [];
let lataus: Lataus = "ladataan";
let suodatin: Suodatin = "kaikki";
let yritetty = false;

/** Kaikki tilan muutokset kulkevat tämän kautta, jotta DOM ei unohdu. */
function muuta(muutos: () => void): void {
  muutos();
  paivita();
}
// @loppu tila

// @alku elementit
function hae<T extends Element>(valitsin: string): T {
  const elementti = document.querySelector<T>(valitsin);
  if (elementti === null) throw new Error(`ei löydy: ${valitsin}`);
  return elementti;
}

function luo<K extends keyof HTMLElementTagNameMap>(
  tagi: K, ominaisuudet: Record<string, string> = {},
  ...lapset: (Node | string)[]
): HTMLElementTagNameMap[K] {
  const elementti = document.createElement(tagi);
  for (const [nimi, arvo] of Object.entries(ominaisuudet)) {
    elementti.setAttribute(nimi, arvo);
  }
  elementti.append(...lapset);
  return elementti;
}

// Pysyvät elementit ovat sivun HTML:ssä (index.html).
const yhteenvetoEl = hae<HTMLElement>(".yhteenveto");
const lomake = hae<HTMLFormElement>(".lisays");
const nimiEl = hae<HTMLInputElement>("#nimi");
const kiireEl = hae<HTMLSelectElement>("#kiire");
const virheEl = hae<HTMLElement>("#nimi-virhe");
const suodatinEl = hae<HTMLFieldSetElement>(".suodatin");

// Tilasta riippuvat elementit luodaan kerran ja liitetään tarvittaessa.
const ladataanEl = luo("p", { class: "tila" }, "Ladataan tehtäviä…");
const latausvirheEl = luo("p", { class: "virhe", role: "alert" },
  "Tehtävien lataus epäonnistui.");
const uudelleenEl = luo("button", { type: "button" }, "Yritä uudelleen");
const tyhjaEl = luo("p", { class: "tila" }, "Ei näytettäviä tehtäviä.");
const listaEl = luo("ul", { class: "tehtavat", "aria-label": "Tehtävät" });
const siivousEl = luo("button", { type: "button" }, "Poista valmiit");
const VALINNAISET =
  [ladataanEl, latausvirheEl, uudelleenEl, tyhjaEl, listaEl, siivousEl];
// @loppu elementit

// @alku rivit
// Jokaista tehtävää vastaa yksi <li>, joka säilyy niin kauan kuin
// tehtäväkin. Tämä taulu on "avain": tehtävän id -> sen elementit.
interface Rivi { li: HTMLLIElement; ruutu: HTMLInputElement }
const rivit = new Map<number, Rivi>();

function luoRivi(t: Tehtava): Rivi {
  const ruutu = luo("input", { type: "checkbox" });
  const poisto = luo("button",
    { type: "button", "aria-label": `Poista ${t.nimi}` }, "Poista");
  const li = luo("li", { class: "tehtava" },
    luo("label", {}, ruutu, " ", luo("span", {}, t.nimi)));
  if (t.kiire === "kiireellinen") {
    li.append(luo("span", { class: "merkki" }, "kiireellinen"));
  }
  li.append(poisto);
  ruutu.addEventListener("change", () => muuta(() => {
    tehtavat = logiikka.vaihda(tehtavat, t.id);
  }));
  poisto.addEventListener("click", () => muuta(() => {
    tehtavat = logiikka.poista(tehtavat, t.id);
  }));
  return { li, ruutu };
}

function paivitaRivit(nakyvat: readonly Tehtava[]): void {
  const halutut = nakyvat.map((t) => {
    let rivi = rivit.get(t.id);
    if (rivi === undefined) {
      rivi = luoRivi(t);
      rivit.set(t.id, rivi);
    }
    rivi.ruutu.checked = t.valmis;
    rivi.li.classList.toggle("valmis", t.valmis);
    return rivi.li;
  });
  // Poistetaan ylimääräiset ja lisätään puuttuvat. Paikallaan olevaan
  // riviin ei kosketa, jotta sen fokus ja valinta säilyvät.
  for (const li of [...listaEl.children]) {
    if (!halutut.includes(li as HTMLLIElement)) li.remove();
  }
  halutut.forEach((li, i) => {
    if (listaEl.children[i] !== li) {
      listaEl.insertBefore(li, listaEl.children[i] ?? null);
    }
  });
  for (const id of rivit.keys()) {
    if (!tehtavat.some((t) => t.id === id)) rivit.delete(id);
  }
}
// @loppu rivit

// @alku paivita
/** Saattaa DOM:n vastaamaan tilaa. Jokainen tilasta riippuva kohta on
 *  muistettava päivittää täällä; unohdus on tämän tyylin tyyppivirhe. */
function paivita(): void {
  const valmis = lataus === "valmis";
  yhteenvetoEl.textContent = valmis ? logiikka.yhteenveto(tehtavat) : "";

  const virhe = yritetty
    ? logiikka.validoi(nimiEl.value, tehtavat) : null;
  virheEl.textContent = virhe ?? "";
  nimiEl.setAttribute("aria-invalid", String(virhe !== null));

  const nakyvat = logiikka.suodata(tehtavat, suodatin);
  paivitaRivit(nakyvat);
  siivousEl.disabled = !tehtavat.some((t) => t.valmis);

  const esilla = new Set<Element>(
    lataus === "ladataan" ? [ladataanEl]
    : lataus === "virhe" ? [latausvirheEl, uudelleenEl]
    : [nakyvat.length === 0 ? tyhjaEl : listaEl, siivousEl]);
  let edellinen: Element = suodatinEl;
  for (const elementti of VALINNAISET) {
    if (!esilla.has(elementti)) { elementti.remove(); continue; }
    if (edellinen.nextElementSibling !== elementti) {
      edellinen.after(elementti);
    }
    edellinen = elementti;
  }

  if (valmis) {                       // sivuvaikutukset
    logiikka.tallenna(localStorage, tehtavat);
    document.title = logiikka.otsikko(tehtavat);
  }
}
// @loppu paivita

// @alku tapahtumat
function lataa(): void {
  muuta(() => { lataus = "ladataan"; });
  logiikka.haeTehtavat(localStorage).then(
    (haetut) => muuta(() => { tehtavat = haetut; lataus = "valmis"; }),
    () => muuta(() => { lataus = "virhe"; }),
  );
}

lomake.addEventListener("submit", (tapahtuma) => {
  tapahtuma.preventDefault();
  muuta(() => {
    if (logiikka.validoi(nimiEl.value, tehtavat) === null) {
      tehtavat = logiikka.lisaa(tehtavat, nimiEl.value,
                                kiireEl.value as Kiire);
      nimiEl.value = "";              // kentän arvo elää DOM:ssa
      yritetty = false;
    } else {
      yritetty = true;
    }
  });
  nimiEl.focus();
});
nimiEl.addEventListener("input", paivita);
suodatinEl.addEventListener("change", (tapahtuma) => muuta(() => {
  suodatin = (tapahtuma.target as HTMLInputElement).value as Suodatin;
}));
uudelleenEl.addEventListener("click", lataa);
siivousEl.addEventListener("click", () => muuta(() => {
  tehtavat = logiikka.poistaValmiit(tehtavat);
}));

lataa();
// @loppu tapahtumat
