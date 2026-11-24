// SSA-muoto: jokaiselle rekisterille täsmälleen yksi määrittely.
#pragma once

#include <iosfwd>
#include <vector>

#include "ir.hpp"

namespace kide {

// Välittömät dominoijat: idom[b] on lähin lohko, jonka kautta jokainen
// polku alkulohkosta b:hen kulkee. idom[0] = 0.
std::vector<int> dominoijat(const IrFunktio& f);

// Muuntaa funktion SSA-muotoon (karsittu SSA, Cytron ym. 1991).
// Funktiossa ei saa olla saavuttamattomia lohkoja.
IrFunktio ssa_muotoon(const IrFunktio& f);

void tulosta_dominanssi(const IrFunktio& f, std::ostream& u);

}  // namespace kide
