// Koodingenerointi RISC-V:lle (RV64IM, LP64-kutsukonventio).
#pragma once

#include <iosfwd>

#include "ir.hpp"
#include "rekisterit.hpp"

namespace kide {

// Kirjoittaa funktion GNU-kokoajan syntaksilla. Kide-funktio f on
// symboli k_f, ja print kutsuu ajonaikaisen kirjaston funktiota
// kide_tulosta.
void generoi(const IrFunktio& f, const Varaus& v, std::ostream& u);

}  // namespace kide
