// Palvelinrenderöinti pienoiskoossa: sama näkymäfunktio, jota selain
// käyttäisi DOM:n päivittämiseen, tuottaa palvelimella HTML-merkkijonon.
// Näkymät on kirjoitettu ilman JSX:ää ja mallipohjia, jotta tiedoston
// voi ajaa Nodella sellaisenaan: createElement ja h ovat ne kutsut,
// joiksi JSX ja mallipohjat käännetään.
import { createElement } from "react";
import { renderToString as reactMerkkijonoksi } from "react-dom/server";
import { createSSRApp, h } from "vue";
import { renderToString as vueMerkkijonoksi } from "vue/server-renderer";
import type { Tehtava } from "../yhteinen/logiikka.ts";

const tehtavat: Tehtava[] = [
  { id: 1, nimi: "Varaa kokoushuone", kiire: "tavallinen", valmis: false },
  { id: 2, nimi: "Tilaa kahvit", kiire: "tavallinen", valmis: true },
];

// @alku nakymat
function ReactNakyma() {
  return createElement("ul", null, tehtavat.map((t) =>
    createElement("li", { key: t.id }, t.nimi)));
}

const VueNakyma = {
  render: () => h("ul", tehtavat.map((t) =>
    h("li", { key: t.id }, t.nimi))),
};
// @loppu nakymat

// @alku palvelin
console.log("React:");
console.log(reactMerkkijonoksi(createElement(ReactNakyma)));
console.log("Vue:");
console.log(await vueMerkkijonoksi(createSSRApp(VueNakyma)));

// Selain saa HTML:n lisäksi tilan, josta se on tehty. Hydraatiossa
// kehys ajaa saman näkymäfunktion tällä tilalla, olettaa tuloksen
// vastaavan valmista HTML:ää ja liittää tapahtumankäsittelijät.
console.log("Tila selaimelle:");
const tunnisteet = JSON.stringify(tehtavat.map((t) => t.id));
console.log(
  `<script type="application/json" id="tila">${tunnisteet}</script>`);
// @loppu palvelin
