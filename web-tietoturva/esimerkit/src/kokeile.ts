// Käynnistää luvun 3 keskustelupalstan omalle koneelle, jotta
// hyökkäyksiä ja puolustuksia voi kokeilla omassa selaimessa.
//
//   node src/kokeile.ts              ei puolustuksia
//   node src/kokeile.ts csp          vain CSP
//   node src/kokeile.ts koodaus csp  molemmat
//
// Palvelin kuuntelee vain osoitetta 127.0.0.1, eli se ei näy muille
// koneille. Lopeta painamalla Ctrl-C.
import { kaynnista } from "./http.ts";
import { palsta } from "./03-xss/xss.ts";

const valinnat = new Set(process.argv.slice(2));
const s = await kaynnista(palsta({ escapoi: valinnat.has("koodaus"),
                                   csp: valinnat.has("csp") }));
const kuva = encodeURIComponent("<img src=x onerror='alert(1)'>");
console.log(`Palsta:        ${s.url}/
Heijastettu:   ${s.url}/?q=${kuva}
DOM-pohjainen: ${s.url}/#${kuva}
Tallennettu:   kirjoita lomakkeeseen <script>alert(1)</script>`);
