// Välikieli: kolmiosoitekoodi peruslohkoissa.
#pragma once

#include <cstdint>
#include <iosfwd>
#include <string>
#include <vector>

namespace kide {

// @alku kasky
enum class Op {
    Vakio, Kopio, Neg, Not,
    Add, Sub, Mul, Div, Rem, Eq, Ne, Lt, Le, Gt, Ge,
    Kutsu, Tulosta, Phi,
    Hyppy, Haara, Palauta,      // päättävät peruslohkon
};

using Vreg = int;                // virtuaalirekisteri; -1 = ei mitään

struct Kasky {
    Op op;
    Vreg kohde = -1;             // tulos
    std::vector<Vreg> lahteet;   // operandit
    std::int64_t vakio = 0;      // Vakio
    std::string funktio;         // Kutsu
    std::vector<int> lohkot;     // Hyppy: [kohde], Haara: [tosi, epätosi],
                                 // Phi: lähteiden edeltäjälohkot
};

struct Peruslohko {
    std::vector<Kasky> kaskyt;   // viimeinen on Hyppy, Haara tai Palauta
    std::vector<int> edeltajat, seuraajat;
};

struct IrFunktio {
    std::string nimi;
    int parametreja = 0;         // parametrit ovat rekisterit 0 .. n-1
    std::vector<std::string> nimet;   // kunkin rekisterin nimi
    std::vector<Peruslohko> lohkot;   // lohko 0 on alkulohko
};
// @loppu kasky

struct IrOhjelma { std::vector<IrFunktio> funktiot; };

bool paattava(Op op);
bool puhdas(Op op);          // ei sivuvaikutuksia: poistettavissa
// Laskee edeltäjä- ja seuraajalistat päättävistä käskyistä.
void laske_reunat(IrFunktio& f);
void tulosta_ir(const IrOhjelma& o, std::ostream& u);
void tulosta_ir(const IrFunktio& f, std::ostream& u);
std::string rekisteri(const IrFunktio& f, Vreg r);

}  // namespace kide
