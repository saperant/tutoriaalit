// Jäsennin: tokenit abstraktiksi syntaksipuuksi.
#pragma once

#include <vector>

#include "ast.hpp"

namespace kide {

// Jäsentää koko ohjelman. Virheet raportoidaan diagnostiikkaan, ja
// jäsennin jatkaa seuraavasta lauseesta (virheistä toipuminen).
Ohjelma jasenna(const std::vector<Tokeni>& tokenit, Diagnostiikka& diag);

}  // namespace kide
