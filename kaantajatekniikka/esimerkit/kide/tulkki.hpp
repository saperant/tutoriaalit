// Puuta kulkeva tulkki: kielen viitetoteutus.
#pragma once

#include <iosfwd>

#include "ast.hpp"

namespace kide {

// Suorittaa tarkistetun ohjelman funktion main. Palauttaa mainin arvon;
// heittää std::runtime_errorin, jos kutsupino kasvaa liian syväksi.
std::int64_t tulkitse(const Ohjelma& ohjelma, std::ostream& ulos);

}  // namespace kide
