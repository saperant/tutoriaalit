#include "tarkistin.hpp"

#include <unordered_map>

namespace kide {

namespace {

struct Allekirjoitus {
    std::vector<Tyyppi> parametrit;
    Tyyppi paluu;
};

// @alku symbolit
// Näkyvyysalueet pinona: sisin alue on viimeisenä. Kukin alue
// kuvaa nimen muuttujan numeroksi funktion sisällä.
class Symbolit {
public:
    void avaa() { alueet_.emplace_back(); }
    void sulje() { alueet_.pop_back(); }

    // Palauttaa false, jos nimi on jo esitelty samalla alueella.
    bool esittele(const std::string& nimi, int muuttuja) {
        return alueet_.back().emplace(nimi, muuttuja).second;
    }
    // Etsii nimen sisimmästä alueesta ulospäin; -1 = tuntematon.
    int etsi(const std::string& nimi) const {
        for (auto a = alueet_.rbegin(); a != alueet_.rend(); ++a) {
            if (auto l = a->find(nimi); l != a->end()) return l->second;
        }
        return -1;
    }

private:
    std::vector<std::unordered_map<std::string, int>> alueet_;
};
// @loppu symbolit

class Tarkistin {
public:
    explicit Tarkistin(Diagnostiikka& d) : diag_(d) {}
    void ohjelma(Ohjelma& o);

private:
    void funktio(Funktio& f);
    void lauseet(Lauseet& ls);
    void lause(Lause& l);
    Tyyppi lauseke(Lauseke& l);
    Tyyppi binaari(Binaari& b, Sijainti s);
    Tyyppi kutsu(Kutsu& k, Sijainti s);
    int uusi_muuttuja(const std::string& nimi, Tyyppi t, Sijainti s);
    void odota(Tyyppi odotettu, Tyyppi saatu, Sijainti s,
               const std::string& mika);

    Diagnostiikka& diag_;
    std::unordered_map<std::string, Allekirjoitus> funktiot_;
    Symbolit symbolit_;
    Funktio* nykyinen_ = nullptr;
    std::vector<Tyyppi> tyypit_;     // nykyisen funktion muuttujat
};

// @alku odota
// Tuntematon tyyppi sopii kaikkeen: virheellisestä alilausekkeesta
// raportoidaan vain kerran, ei jokaisessa sitä käyttävässä lausekkeessa.
void Tarkistin::odota(Tyyppi odotettu, Tyyppi saatu, Sijainti s,
                      const std::string& mika) {
    if (odotettu == Tyyppi::Tuntematon || saatu == Tyyppi::Tuntematon
        || odotettu == saatu) {
        return;
    }
    diag_.virhe(s, mika + " odottaa tyyppiä " + nimi(odotettu)
                       + ", saatiin " + nimi(saatu));
}
// @loppu odota

// @alku ohjelma
void Tarkistin::ohjelma(Ohjelma& o) {
    // Ensin kaikkien funktioiden allekirjoitukset, jotta funktiot voivat
    // kutsua toisiaan järjestyksestä riippumatta.
    for (const auto& f : o.funktiot) {
        Allekirjoitus a{{}, f.paluutyyppi};
        for (const auto& p : f.parametrit) a.parametrit.push_back(p.tyyppi);
        if (!funktiot_.emplace(f.nimi, a).second) {
            diag_.virhe(f.sijainti, "funktio '" + f.nimi
                                        + "' on jo määritelty");
        }
        if (f.parametrit.size() > kParametrejaEnintaan) {
            diag_.virhe(f.sijainti, "funktiolla voi olla enintään 8 "
                                    "parametria");
        }
    }
    auto m = funktiot_.find("main");
    if (m == funktiot_.end() || !m->second.parametrit.empty()
        || m->second.paluu != Tyyppi::Int) {
        diag_.virhe({1, 1}, "ohjelmasta puuttuu funktio main() -> int");
    }
    for (auto& f : o.funktiot) funktio(f);
}
// @loppu ohjelma

// @alku palauttaa
// Palauttaako lauseiden jono arvon kaikilla poluilla?
bool palauttaa(const Lauseet& ls);

bool palauttaa(const Lause& l) {
    if (std::holds_alternative<Palauta>(l.v)) return true;
    if (auto* j = std::get_if<Jos>(&l.v)) {
        return palauttaa(j->tosi) && palauttaa(j->epatosi);
    }
    if (auto* b = std::get_if<Lohko>(&l.v)) return palauttaa(b->lauseet);
    return false;   // while-silmukan runkoa ei välttämättä suoriteta
}

bool palauttaa(const Lauseet& ls) {
    for (const auto& l : ls) {
        if (palauttaa(*l)) return true;
    }
    return false;
}
// @loppu palauttaa

int Tarkistin::uusi_muuttuja(const std::string& nimi, Tyyppi t,
                             Sijainti s) {
    int n = static_cast<int>(nykyinen_->muuttujat.size());
    nykyinen_->muuttujat.push_back(nimi);
    tyypit_.push_back(t);
    if (!symbolit_.esittele(nimi, n)) {
        diag_.virhe(s, "'" + nimi + "' on jo esitelty tällä alueella");
    }
    return n;
}

void Tarkistin::funktio(Funktio& f) {
    nykyinen_ = &f;
    tyypit_.clear();
    symbolit_.avaa();
    for (const auto& p : f.parametrit) {
        uusi_muuttuja(p.nimi, p.tyyppi, p.sijainti);
    }
    lauseet(f.runko);
    symbolit_.sulje();
    if (!palauttaa(f.runko)) {
        diag_.virhe(f.sijainti, "funktio '" + f.nimi
                                    + "' voi päättyä ilman return-lausetta");
    }
}

void Tarkistin::lauseet(Lauseet& ls) {
    for (auto& l : ls) lause(*l);
}

void Tarkistin::lause(Lause& l) {
    std::visit(Kaikki{
        // @alku esittely
        [&](Esittely& x) {
            // Arvo tarkistetaan ennen esittelyä: var x = x + 1; viittaa
            // ulomman alueen muuttujaan x.
            Tyyppi t = lauseke(*x.arvo);
            x.muuttuja = uusi_muuttuja(x.nimi, t, l.sijainti);
        },
        // @loppu esittely
        [&](Sijoitus& x) {
            Tyyppi t = lauseke(*x.arvo);
            x.muuttuja = symbolit_.etsi(x.nimi);
            if (x.muuttuja < 0) {
                diag_.virhe(l.sijainti, "tuntematon muuttuja '" + x.nimi
                                            + "'");
                return;
            }
            odota(tyypit_[x.muuttuja], t, x.arvo->sijainti,
                  "muuttuja '" + x.nimi + "'");
        },
        [&](Jos& x) {
            odota(Tyyppi::Bool, lauseke(*x.ehto), x.ehto->sijainti,
                  "if-ehto");
            symbolit_.avaa();
            lauseet(x.tosi);
            symbolit_.sulje();
            symbolit_.avaa();
            lauseet(x.epatosi);
            symbolit_.sulje();
        },
        [&](Kun& x) {
            odota(Tyyppi::Bool, lauseke(*x.ehto), x.ehto->sijainti,
                  "while-ehto");
            symbolit_.avaa();
            lauseet(x.runko);
            symbolit_.sulje();
        },
        [&](Palauta& x) {
            odota(nykyinen_->paluutyyppi, lauseke(*x.arvo),
                  x.arvo->sijainti, "return");
        },
        [&](Tulosta& x) {
            odota(Tyyppi::Int, lauseke(*x.arvo), x.arvo->sijainti,
                  "print");
        },
        [&](LausekeLause& x) { lauseke(*x.lauseke); },
        [&](Lohko& x) {
            symbolit_.avaa();
            lauseet(x.lauseet);
            symbolit_.sulje();
        },
    }, l.v);
}

// @alku lauseke
Tyyppi Tarkistin::lauseke(Lauseke& l) {
    l.tyyppi = std::visit(Kaikki{
        [](Luku&) { return Tyyppi::Int; },
        [](Totuus&) { return Tyyppi::Bool; },
        [&](Nimi& x) {
            x.muuttuja = symbolit_.etsi(x.nimi);
            if (x.muuttuja < 0) {
                diag_.virhe(l.sijainti, "tuntematon muuttuja '" + x.nimi
                                            + "'");
                return Tyyppi::Tuntematon;
            }
            return tyypit_[x.muuttuja];
        },
        [&](Unaari& x) {
            Tyyppi t = x.op == Laji::Miinus ? Tyyppi::Int : Tyyppi::Bool;
            odota(t, lauseke(*x.a), l.sijainti, kuvaus(x.op));
            return t;
        },
        [&](Binaari& x) { return binaari(x, l.sijainti); },
        [&](Kutsu& x) { return kutsu(x, l.sijainti); },
    }, l.v);
    return l.tyyppi;
}
// @loppu lauseke

Tyyppi Tarkistin::binaari(Binaari& b, Sijainti s) {
    Tyyppi v = lauseke(*b.vasen);
    Tyyppi o = lauseke(*b.oikea);
    switch (b.op) {
    case Laji::Yhtasuuri:
    case Laji::Erisuuri:     // int == int tai bool == bool
        odota(v, o, s, kuvaus(b.op));
        return Tyyppi::Bool;
    case Laji::Ja:
    case Laji::Tai:
        odota(Tyyppi::Bool, v, s, kuvaus(b.op));
        odota(Tyyppi::Bool, o, s, kuvaus(b.op));
        return Tyyppi::Bool;
    case Laji::Pienempi:
    case Laji::PienempiYhta:
    case Laji::Suurempi:
    case Laji::SuurempiYhta:
        odota(Tyyppi::Int, v, s, kuvaus(b.op));
        odota(Tyyppi::Int, o, s, kuvaus(b.op));
        return Tyyppi::Bool;
    default:                 // + - * / %
        odota(Tyyppi::Int, v, s, kuvaus(b.op));
        odota(Tyyppi::Int, o, s, kuvaus(b.op));
        return Tyyppi::Int;
    }
}

// @alku kutsu
Tyyppi Tarkistin::kutsu(Kutsu& k, Sijainti s) {
    std::vector<Tyyppi> annetut;
    for (auto& a : k.argumentit) annetut.push_back(lauseke(*a));
    auto f = funktiot_.find(k.funktio);
    if (f == funktiot_.end()) {
        diag_.virhe(s, "tuntematon funktio '" + k.funktio + "'");
        return Tyyppi::Tuntematon;
    }
    const auto& odotetut = f->second.parametrit;
    if (annetut.size() != odotetut.size()) {
        diag_.virhe(s, "funktio '" + k.funktio + "' odottaa "
                           + std::to_string(odotetut.size())
                           + " argumenttia, saatiin "
                           + std::to_string(annetut.size()));
    } else {
        for (std::size_t i = 0; i < annetut.size(); ++i) {
            odota(odotetut[i], annetut[i], k.argumentit[i]->sijainti,
                  "argumentti " + std::to_string(i + 1));
        }
    }
    return f->second.paluu;
}
// @loppu kutsu

}  // namespace

void tarkista(Ohjelma& ohjelma, Diagnostiikka& diag) {
    Tarkistin(diag).ohjelma(ohjelma);
}

}  // namespace kide
