// Optimoinnit, jotka toimivat SSA-muodossa (-O2).
#pragma once

#include <iosfwd>
#include <string>

#include "ir.hpp"

namespace kide {

// Tarkistaa SSA-muodon ehdot: yksi määrittely rekisteriä kohden, jokainen
// määrittely dominoi käyttöjään ja phit vastaavat lohkon edeltäjiä.
// Palauttaa ensimmäisen virheen kuvauksen tai tyhjän merkkijonon.
std::string tarkista_ssa(const IrFunktio& f);

// Poistaa lohkot, joihin ei enää pääse, ja korjaa phit vastaamaan
// jäljelle jääneitä kaaria. Palauttaa true, jos jotain muuttui.
bool siisti_ssa(IrFunktio& f);

// Kukin passi vaatii SSA-muotoisen funktion, säilyttää SSA-muodon ja
// palauttaa true, jos se muutti funktiota.
bool etene_vakiot(IrFunktio& f);        // harva ehdollinen eteneminen
bool numeroi_arvot_ssa(IrFunktio& f);   // globaali arvonumerointi
bool poista_kuollut_ssa(IrFunktio& f);  // merkitse ja lakaise

// Ajaa passit kiintopisteeseen ja tarkistaa SSA-muodon jokaisen
// muutoksen jälkeen. Jos loki on annettu, funktio tulostetaan
// jokaisen muutoksen tehneen passin jälkeen.
void optimoi_ssa(IrFunktio& f, std::ostream* loki = nullptr);

}  // namespace kide
