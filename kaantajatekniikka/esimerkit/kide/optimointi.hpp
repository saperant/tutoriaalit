// Välikielen optimoinnit.
#pragma once

#include <iosfwd>

#include "ir.hpp"

namespace kide {

// Kukin passi palauttaa true, jos se muutti funktiota.
bool poista_saavuttamattomat(IrFunktio& f);
bool numeroi_arvot(IrFunktio& f);     // laskostus, kopiot, yhteiset
bool siisti_ohjausvuo(IrFunktio& f);  // tyhjät lohkot ja ketjut
bool poista_kuollut_koodi(IrFunktio& f);
bool yhdista_kopiot(IrFunktio& f);    // t = a + b; x = t  =>  x = a + b

// Ajaa passit kiintopisteeseen. Jos loki on annettu, funktio tulostetaan
// jokaisen muutoksen tehneen passin jälkeen.
void optimoi(IrFunktio& f, std::ostream* loki = nullptr);

}  // namespace kide
