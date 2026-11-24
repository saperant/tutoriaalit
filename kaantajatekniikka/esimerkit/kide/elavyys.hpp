// Elävyysanalyysi (liveness): mitkä rekisterit ovat vielä käytössä.
#pragma once

#include <iosfwd>
#include <vector>

#include "ir.hpp"

namespace kide {

// @alku elavyys
struct Elavyys {
    // sisaan[b][r]: rekisterin r arvoa voidaan lukea lohkon b alusta
    // lähtien ennen kuin se kirjoitetaan uudelleen. ulos[b] vastaavasti
    // lohkon lopussa.
    std::vector<std::vector<bool>> sisaan, ulos;
    int kierroksia = 0;          // iteraatiokierroksia kiintopisteeseen
};
// @loppu elavyys

Elavyys laske_elavyys(const IrFunktio& f);
void tulosta_elavyys(const IrFunktio& f, const Elavyys& e, std::ostream& u);

}  // namespace kide
