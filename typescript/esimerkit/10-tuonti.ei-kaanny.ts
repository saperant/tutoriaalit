// verbatimModuleSyntax: tyyppi tuodaan type-merkinnällä, jotta tuonti
// voidaan poistaa ajosta yksinkertaisesti tiedostoa katsomalla.
import { parse, ParsedPath } from "node:path"; // @virhe
import { parse as jasenna, type ParsedPath as Osat } from "node:path";

const osat: Osat = jasenna("/var/log/tilaukset.2026-11.log");
console.log(osat.name, osat.ext);
