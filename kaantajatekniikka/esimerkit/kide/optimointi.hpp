// Välikielen optimoinnit.
#pragma once

#include <cstdint>
#include <iosfwd>
#include <optional>

#include "ir.hpp"

namespace kide {

// Laskee operaation käännösaikana; nullopt, jos op ei ole laskutoimitus.
std::optional<std::int64_t> laskosta(Op op, std::int64_t a, std::int64_t b);
bool vaihdannainen(Op op);       // a op b == b op a

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
