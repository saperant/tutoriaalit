#include "alennus.hpp"

#include <stdexcept>

namespace kide {

namespace {

class Alentaja {
public:
    explicit Alentaja(const Funktio& f);
    IrFunktio tulos();

private:
    // @alku apu
    Vreg uusi_valiaikainen() {
        f_.nimet.push_back("%" + std::to_string(++valiaikaisia_));
        return static_cast<Vreg>(f_.nimet.size()) - 1;
    }
    int uusi_lohko() {
        f_.lohkot.emplace_back();
        return static_cast<int>(f_.lohkot.size()) - 1;
    }
    void aloita(int lohko) {
        nykyinen_ = lohko;
        jarjestys_.push_back(lohko);   // lohkojen lopullinen järjestys
    }
    void lisaa(Kasky k) {
        f_.lohkot[nykyinen_].kaskyt.push_back(std::move(k));
    }
    Vreg laske(Op op, std::vector<Vreg> lahteet) {
        Vreg t = uusi_valiaikainen();
        lisaa({.op = op, .kohde = t, .lahteet = std::move(lahteet)});
        return t;
    }
    Vreg vakio(std::int64_t arvo) {
        Vreg t = uusi_valiaikainen();
        lisaa({.op = Op::Vakio, .kohde = t, .vakio = arvo});
        return t;
    }
    void kopioi(Vreg kohde, Vreg lahde) {
        lisaa({.op = Op::Kopio, .kohde = kohde, .lahteet = {lahde}});
    }
    void hyppaa(int lohko) { lisaa({.op = Op::Hyppy, .lohkot = {lohko}}); }
    // @loppu apu

    void lauseet(const Lauseet& ls);
    void lause(const Lause& l);
    Vreg arvo(const Lauseke& l);
    Vreg oikosulku(const Binaari& b);
    void ehto(const Lauseke& l, int tosi, int epatosi);

    IrFunktio f_;
    std::vector<Vreg> muuttujat_;   // lähdekoodin muuttuja -> rekisteri
    std::vector<int> jarjestys_;
    int nykyinen_ = 0;
    int valiaikaisia_ = 0;
};

// Lähdekoodin muuttujat ovat rekisterit 0 .. n-1. Saman nimiset
// (eri alueilla esitellyt) erotetaan jälkiliitteellä #2, #3 ...
Alentaja::Alentaja(const Funktio& f) {
    f_.nimi = f.nimi;
    f_.parametreja = static_cast<int>(f.parametrit.size());
    for (std::size_t i = 0; i < f.muuttujat.size(); ++i) {
        int sama = 1;
        const std::string& n = f.muuttujat[i];
        for (std::size_t j = 0; j < i; ++j) sama += f.muuttujat[j] == n;
        f_.nimet.push_back(sama == 1 ? n : n + "#" + std::to_string(sama));
        muuttujat_.push_back(static_cast<Vreg>(i));
    }
    aloita(uusi_lohko());
    lauseet(f.runko);
}

IrFunktio Alentaja::tulos() {
    // Tarkistin takaa, että jokainen polku palauttaa arvon, joten
    // viimeiseen lohkoon ei päädytä. Se tarvitsee silti päättävän käskyn.
    if (f_.lohkot[nykyinen_].kaskyt.empty()
        || !paattava(f_.lohkot[nykyinen_].kaskyt.back().op)) {
        lisaa({.op = Op::Palauta, .lahteet = {vakio(0)}});
    }
    // Numeroidaan lohkot uudelleen siinä järjestyksessä, jossa ne
    // aloitettiin: silloin silmukan runko on ehdon perässä ja niin edelleen.
    std::vector<int> uusi(f_.lohkot.size(), -1);
    for (std::size_t i = 0; i < jarjestys_.size(); ++i) {
        uusi[jarjestys_[i]] = static_cast<int>(i);
    }
    std::vector<Peruslohko> lohkot(jarjestys_.size());
    for (std::size_t i = 0; i < f_.lohkot.size(); ++i) {
        if (uusi[i] < 0) throw std::logic_error("lohkoa ei aloitettu");
        for (Kasky& k : f_.lohkot[i].kaskyt) {
            for (int& b : k.lohkot) b = uusi[b];
        }
        lohkot[uusi[i]] = std::move(f_.lohkot[i]);
    }
    f_.lohkot = std::move(lohkot);
    laske_reunat(f_);
    return std::move(f_);
}

void Alentaja::lauseet(const Lauseet& ls) {
    for (const auto& l : ls) lause(*l);
}

void Alentaja::lause(const Lause& l) {
    std::visit(Kaikki{
        [&](const Esittely& x) {
            kopioi(muuttujat_[x.muuttuja], arvo(*x.arvo));
        },
        [&](const Sijoitus& x) {
            kopioi(muuttujat_[x.muuttuja], arvo(*x.arvo));
        },
        [&](const Jos& x) {
            int tosi = uusi_lohko();
            int loppu = uusi_lohko();
            int epatosi = x.epatosi.empty() ? loppu : uusi_lohko();
            ehto(*x.ehto, tosi, epatosi);
            aloita(tosi);
            lauseet(x.tosi);
            hyppaa(loppu);
            if (!x.epatosi.empty()) {
                aloita(epatosi);
                lauseet(x.epatosi);
                hyppaa(loppu);
            }
            aloita(loppu);
        },
        // @alku kun
        [&](const Kun& x) {
            int testi = uusi_lohko();
            int runko = uusi_lohko();
            int loppu = uusi_lohko();
            hyppaa(testi);
            aloita(testi);
            ehto(*x.ehto, runko, loppu);
            aloita(runko);
            lauseet(x.runko);
            hyppaa(testi);
            aloita(loppu);
        },
        [&](const Palauta& x) {
            lisaa({.op = Op::Palauta, .lahteet = {arvo(*x.arvo)}});
            aloita(uusi_lohko());     // mahdollinen kuollut koodi
        },
        // @loppu kun
        [&](const Tulosta& x) {
            lisaa({.op = Op::Tulosta, .lahteet = {arvo(*x.arvo)}});
        },
        [&](const LausekeLause& x) { arvo(*x.lauseke); },
        [&](const Lohko& x) { lauseet(x.lauseet); },
    }, l.v);
}

// @alku ehto
// Hyppykoodi: ehto haarautuu suoraan kohdelohkoihin, eikä totuusarvoa
// tarvitse laskea rekisteriin. a && b hyppää epätoteen jo a:n kohdalla.
void Alentaja::ehto(const Lauseke& l, int tosi, int epatosi) {
    if (const auto* b = std::get_if<Binaari>(&l.v)) {
        if (b->op == Laji::Ja || b->op == Laji::Tai) {
            int keski = uusi_lohko();
            if (b->op == Laji::Ja) {
                ehto(*b->vasen, keski, epatosi);
            } else {
                ehto(*b->vasen, tosi, keski);
            }
            aloita(keski);
            ehto(*b->oikea, tosi, epatosi);
            return;
        }
    }
    if (const auto* u = std::get_if<Unaari>(&l.v); u && u->op == Laji::Ei) {
        ehto(*u->a, epatosi, tosi);
        return;
    }
    lisaa({.op = Op::Haara, .lahteet = {arvo(l)}, .lohkot = {tosi, epatosi}});
}
// @loppu ehto

Op binaarioperaatio(Laji laji) {
    switch (laji) {
    case Laji::Plus: return Op::Add;
    case Laji::Miinus: return Op::Sub;
    case Laji::Tahti: return Op::Mul;
    case Laji::Kautta: return Op::Div;
    case Laji::Prosentti: return Op::Rem;
    case Laji::Yhtasuuri: return Op::Eq;
    case Laji::Erisuuri: return Op::Ne;
    case Laji::Pienempi: return Op::Lt;
    case Laji::PienempiYhta: return Op::Le;
    case Laji::Suurempi: return Op::Gt;
    case Laji::SuurempiYhta: return Op::Ge;
    default: throw std::logic_error("ei binäärioperaattori");
    }
}

Vreg Alentaja::arvo(const Lauseke& l) {
    return std::visit(Kaikki{
        [&](const Luku& x) { return vakio(x.arvo); },
        [&](const Totuus& x) { return vakio(x.arvo); },
        [&](const Nimi& x) { return muuttujat_[x.muuttuja]; },
        [&](const Unaari& x) {
            Vreg a = arvo(*x.a);
            return laske(x.op == Laji::Miinus ? Op::Neg : Op::Not, {a});
        },
        [&](const Binaari& x) {
            if (x.op == Laji::Ja || x.op == Laji::Tai) return oikosulku(x);
            Vreg a = arvo(*x.vasen);
            Vreg b = arvo(*x.oikea);
            return laske(binaarioperaatio(x.op), {a, b});
        },
        [&](const Kutsu& x) {
            std::vector<Vreg> argumentit;
            for (const auto& a : x.argumentit) argumentit.push_back(arvo(*a));
            Vreg t = laske(Op::Kutsu, std::move(argumentit));
            f_.lohkot[nykyinen_].kaskyt.back().funktio = x.funktio;
            return t;
        },
    }, l.v);
}

// @alku arvo
// Arvona käytetty a && b: tulos kirjoitetaan kahdessa lohkossa samaan
// rekisteriin. Välikieli ei siis ole SSA-muodossa.
Vreg Alentaja::oikosulku(const Binaari& b) {
    Vreg t = uusi_valiaikainen();
    int oikea = uusi_lohko();
    int loppu = uusi_lohko();
    Vreg a = arvo(*b.vasen);
    kopioi(t, a);
    if (b.op == Laji::Ja) {
        lisaa({.op = Op::Haara, .lahteet = {a}, .lohkot = {oikea, loppu}});
    } else {
        lisaa({.op = Op::Haara, .lahteet = {a}, .lohkot = {loppu, oikea}});
    }
    aloita(oikea);
    kopioi(t, arvo(*b.oikea));
    hyppaa(loppu);
    aloita(loppu);
    return t;
}
// @loppu arvo

}  // namespace

IrOhjelma alenna(const Ohjelma& ohjelma) {
    IrOhjelma tulos;
    for (const auto& f : ohjelma.funktiot) {
        tulos.funktiot.push_back(Alentaja(f).tulos());
    }
    return tulos;
}

}  // namespace kide
