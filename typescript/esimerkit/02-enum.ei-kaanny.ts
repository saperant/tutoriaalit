// enum tuottaa ajonaikaista koodia, joten Node ei voi vain poistaa sitä.
enum Tila { Uusi, Toimitettu } // @virhe: ei poistettavaa syntaksia

// Tilalle: vakio-olio ja siitä johdettu literaaliunioni.
const TILAT = ["uusi", "toimitettu"] as const;
type TilausTila = (typeof TILAT)[number]; // "uusi" | "toimitettu"

const t: TilausTila = "toimitettu";
console.log(t, TILAT.indexOf(t));
