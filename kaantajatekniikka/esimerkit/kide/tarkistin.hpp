// Semanttinen analyysi: nimet, näkyvyysalueet ja tyypit.
#pragma once

#include "ast.hpp"

namespace kide {

// Sitoo jokaisen nimen esittelyynsä (Nimi::muuttuja), päättelee
// lausekkeiden tyypit ja raportoi virheet. Kirjoittaa tulokset puuhun.
void tarkista(Ohjelma& ohjelma, Diagnostiikka& diag);

constexpr int kParametrejaEnintaan = 8;   // RISC-V:n a0-a7

}  // namespace kide
