// Välikielen tekstimuodon lukija: sama muoto, jonka tulosta_ir kirjoittaa.
#pragma once

#include <iosfwd>

#include "ir.hpp"

namespace kide {

// Lukee yhden tai useamman funktion. Heittää std::runtime_error-
// poikkeuksen, jossa on rivinumero, jos teksti ei ole välikieltä.
IrOhjelma lue_ir(std::istream& syote);

}  // namespace kide
