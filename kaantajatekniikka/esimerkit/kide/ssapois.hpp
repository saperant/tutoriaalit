// SSA-muodosta poistuminen: phit kopioiksi ja kopiot pois.
#pragma once

#include "ir.hpp"

namespace kide {

// Jakaa kriittiset kaaret (lähteellä useita seuraajia ja kohteella
// useita edeltäjiä) uudella lohkolla, johon phin kopiot voi sijoittaa.
// Palauttaa true, jos jokin kaari jaettiin.
bool jaa_kriittiset_kaaret(IrFunktio& f);

enum class Kopiointi { Rinnakkain, Perakkain };

// Korvaa phit kopioilla edeltäjälohkojen lopussa. Perakkain on naiivi
// toteutus, joka on olemassa vain testejä varten: se laskee väärin,
// kun saman lohkon phit lukevat toistensa kohteita.
void pura_phit(IrFunktio& f, Kopiointi tapa = Kopiointi::Rinnakkain);

// Yhdistää kopion lähteen ja kohteen samaksi rekisteriksi, jos ne eivät
// ole koskaan yhtä aikaa käytössä. Palauttaa true, jos jotain muuttui.
bool sulauta_kopiot(IrFunktio& f);

// Koko poistuminen: kaarten jako, phien purku ja kopioiden sulautus.
void ssa_pois(IrFunktio& f);

}  // namespace kide
