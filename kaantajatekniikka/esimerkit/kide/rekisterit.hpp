// Rekisterien varaus: virtuaalirekistereille fyysiset paikat.
#pragma once

#include <iosfwd>
#include <vector>

#include "ir.hpp"

namespace kide {

// @alku paikka
// Varattavat rekisterit ovat kutsun säilyttämät (callee-saved) s1-s11,
// joten arvot säilyvät kutsujen yli ilman erillistä tallennusta.
constexpr int kRekistereita = 11;

struct Paikka {
    int rekisteri = -1;          // 1..11 = s1..s11
    int pinopaikka = -1;         // 0, 1, ... pinokehyksessä
};

struct Varaus {
    std::vector<Paikka> paikat;  // virtuaalirekisteri -> paikka
    int pinopaikkoja = 0;
    std::vector<int> kaytetyt;   // tallennettavat s-rekisterit
};

struct Elinvali {
    Vreg rekisteri;
    int alku, loppu;             // käskyjen sijainteja (2 per käsky)
};
// @loppu paikka

// Elinvälit lohkojen nykyisessä järjestyksessä.
std::vector<Elinvali> elinvalit(const IrFunktio& f);

Varaus varaa_pinoon(const IrFunktio& f);
Varaus varaa_lineaarisesti(const IrFunktio& f, int rekistereita);

void tulosta_varaus(const IrFunktio& f, const Varaus& v, std::ostream& u);

}  // namespace kide
