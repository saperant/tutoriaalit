// Abstrakti syntaksipuu.
#pragma once

#include <cstdint>
#include <iosfwd>
#include <memory>
#include <string>
#include <variant>
#include <vector>

#include "lekseri.hpp"

namespace kide {

// @alku kaikki
// Apuluokka std::visitille: kokoaa lambdat yhdeksi kutsuttavaksi
// olioksi, jolla on yksi operator() kutakin vaihtoehtoa varten.
template <class... F> struct Kaikki : F... { using F::operator()...; };
// @loppu kaikki

enum class Tyyppi { Tuntematon, Int, Bool };
std::string nimi(Tyyppi t);

// @alku lausekkeet
struct Lauseke;
using LausekeP = std::unique_ptr<Lauseke>;

struct Luku { std::int64_t arvo; };
struct Totuus { bool arvo; };
struct Nimi {
    std::string nimi;
    int muuttuja = -1;          // semanttinen analyysi täyttää
};
struct Unaari { Laji op; LausekeP a; };
struct Binaari { Laji op; LausekeP vasen, oikea; };
struct Kutsu {
    std::string funktio;
    std::vector<LausekeP> argumentit;
};

struct Lauseke {
    std::variant<Luku, Totuus, Nimi, Unaari, Binaari, Kutsu> v;
    Sijainti sijainti;
    Tyyppi tyyppi = Tyyppi::Tuntematon;  // semanttinen analyysi täyttää
};
// @loppu lausekkeet

// @alku lauseet
struct Lause;
using LauseP = std::unique_ptr<Lause>;
using Lauseet = std::vector<LauseP>;

struct Esittely {               // var nimi = arvo;
    std::string nimi;
    LausekeP arvo;
    int muuttuja = -1;
};
struct Sijoitus {               // nimi = arvo;
    std::string nimi;
    LausekeP arvo;
    int muuttuja = -1;
};
struct Jos { LausekeP ehto; Lauseet tosi, epatosi; };    // if
struct Kun { LausekeP ehto; Lauseet runko; };            // while
struct Palauta { LausekeP arvo; };                       // return
struct Tulosta { LausekeP arvo; };                       // print
struct LausekeLause { LausekeP lauseke; };               // f(x);
struct Lohko { Lauseet lauseet; };                       // { ... }

struct Lause {
    std::variant<Esittely, Sijoitus, Jos, Kun, Palauta, Tulosta,
                 LausekeLause, Lohko> v;
    Sijainti sijainti;
};
// @loppu lauseet

// @alku ohjelma
struct Parametri {
    std::string nimi;
    Tyyppi tyyppi;
    Sijainti sijainti;
};

struct Funktio {
    std::string nimi;
    std::vector<Parametri> parametrit;  // muuttujat 0 .. n-1
    Tyyppi paluutyyppi;
    Lauseet runko;
    Sijainti sijainti;
    std::vector<std::string> muuttujat;  // semanttinen analyysi täyttää
};

struct Ohjelma { std::vector<Funktio> funktiot; };
// @loppu ohjelma

// Tulostaa puun S-lausekkeina (sulkumuoto).
void tulosta_ast(const Ohjelma& ohjelma, std::ostream& ulos);

}  // namespace kide
