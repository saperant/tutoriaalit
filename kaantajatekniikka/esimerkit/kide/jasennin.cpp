#include "jasennin.hpp"

#include <utility>

namespace kide {

namespace {

// Heitetään, kun jäsennin ei voi jatkaa. Siepataan lause- tai
// funktiotasolla, jossa jäsennin synkronoituu (paniikkitila).
struct Jasennysvirhe {};

// @alku sitovuus
// Binäärioperaattorien sitovuus (binding power); 0 = ei binääri.
int sitovuus(Laji laji) {
    switch (laji) {
    case Laji::Tai: return 1;
    case Laji::Ja: return 2;
    case Laji::Yhtasuuri:
    case Laji::Erisuuri: return 3;
    case Laji::Pienempi:
    case Laji::PienempiYhta:
    case Laji::Suurempi:
    case Laji::SuurempiYhta: return 4;
    case Laji::Plus:
    case Laji::Miinus: return 5;
    case Laji::Tahti:
    case Laji::Kautta:
    case Laji::Prosentti: return 6;
    default: return 0;
    }
}
constexpr int kUnaari = 7;     // -x ja !x sitovat binäärejä tiukemmin
constexpr int kSyvyys = 200;   // sisäkkäisyyden yläraja
// @loppu sitovuus

// @alku vartija
// Laskee rekursion syvyyttä; purkaja vähentää myös poikkeuksessa.
struct Vartija {
    explicit Vartija(int& n) : n_(n) { ++n_; }
    ~Vartija() { --n_; }
    Vartija(const Vartija&) = delete;
    Vartija& operator=(const Vartija&) = delete;
    int& n_;
};
// @loppu vartija

class Jasennin {
public:
    Jasennin(const std::vector<Tokeni>& t, Diagnostiikka& d)
        : tokenit_(t), diag_(d) {}
    Ohjelma ohjelma();

private:
    const Tokeni& nyt() const { return tokenit_[kohta_]; }
    const Tokeni& katso(std::size_t n) const {
        std::size_t i = kohta_ + n;
        return i < tokenit_.size() ? tokenit_[i] : tokenit_.back();
    }
    bool on(Laji laji) const { return nyt().laji == laji; }
    const Tokeni& kuluta() {
        const Tokeni& t = tokenit_[kohta_];
        if (t.laji != Laji::Loppu) ++kohta_;
        return t;
    }
    bool vastaa(Laji laji) {
        if (!on(laji)) return false;
        kuluta();
        return true;
    }
    const Tokeni& odota(Laji laji, const char* mita = nullptr);
    [[noreturn]] void virhe(const std::string& odotettiin);

    Funktio funktio();
    Tyyppi tyyppi();
    Lauseet lohko();
    LauseP lause();
    LauseP jos();
    LausekeP lauseke(int minimi = 0);
    LausekeP etuliite();
    void synkronoi();
    void tarkista_syvyys();

    template <class T> LausekeP uusi(T arvo, Sijainti s) {
        return std::make_unique<Lauseke>(Lauseke{std::move(arvo), s});
    }
    template <class T> LauseP lause(T arvo, Sijainti s) {
        return std::make_unique<Lause>(Lause{std::move(arvo), s});
    }

    const std::vector<Tokeni>& tokenit_;
    Diagnostiikka& diag_;
    std::size_t kohta_ = 0;
    int syvyys_ = 0;
};

// @alku odota
void Jasennin::virhe(const std::string& odotettiin) {
    std::string saatiin = on(Laji::Loppu) || on(Laji::Luku)
                              || on(Laji::Tunniste)
                              ? kuvaus(nyt().laji)
                              : "'" + nyt().teksti + "'";
    if (on(Laji::Tunniste)) saatiin += " '" + nyt().teksti + "'";
    diag_.virhe(nyt().sijainti,
                "odotettiin " + odotettiin + ", saatiin " + saatiin);
    throw Jasennysvirhe{};
}

const Tokeni& Jasennin::odota(Laji laji, const char* mita) {
    if (!on(laji)) virhe(mita ? mita : kuvaus(laji));
    return kuluta();
}
// @loppu odota

// @alku synkronoi
// Paniikkitila: ohitetaan tokeneita, kunnes edellinen lause päättyi
// puolipisteeseen tai seuraava alkaa avainsanalla.
void Jasennin::synkronoi() {
    while (!on(Laji::Loppu)) {
        if (kuluta().laji == Laji::Puolipiste) return;
        switch (nyt().laji) {
        case Laji::Fn: case Laji::Var: case Laji::If: case Laji::While:
        case Laji::Return: case Laji::Print: case Laji::OikeaAalto:
            return;
        default:
            break;
        }
    }
}
// @loppu synkronoi

// @alku ohjelma
Ohjelma Jasennin::ohjelma() {
    Ohjelma tulos;
    while (!on(Laji::Loppu)) {
        try {
            tulos.funktiot.push_back(funktio());
        } catch (const Jasennysvirhe&) {
            // Funktion otsikko oli rikki: seuraavaan fn-sanaan.
            while (!on(Laji::Loppu) && !on(Laji::Fn)) kuluta();
        }
    }
    return tulos;
}

Funktio Jasennin::funktio() {
    Funktio f;
    f.sijainti = odota(Laji::Fn, "funktion määrittelyä").sijainti;
    f.nimi = odota(Laji::Tunniste, "funktion nimeä").teksti;
    odota(Laji::VasenSulku);
    if (!on(Laji::OikeaSulku)) {
        do {
            const Tokeni& n = odota(Laji::Tunniste, "parametrin nimeä");
            odota(Laji::Kaksoispiste);
            f.parametrit.push_back({n.teksti, tyyppi(), n.sijainti});
        } while (vastaa(Laji::Pilkku));
    }
    odota(Laji::OikeaSulku);
    odota(Laji::Nuoli);
    f.paluutyyppi = tyyppi();
    f.runko = lohko();
    return f;
}

Tyyppi Jasennin::tyyppi() {
    if (vastaa(Laji::Int)) return Tyyppi::Int;
    if (vastaa(Laji::Bool)) return Tyyppi::Bool;
    virhe("tyyppiä");
}
// @loppu ohjelma

// @alku lohko
void Jasennin::tarkista_syvyys() {
    if (syvyys_ > kSyvyys) {
        diag_.virhe(nyt().sijainti, "sisäkkäisyys on liian syvä");
        throw Jasennysvirhe{};
    }
}

Lauseet Jasennin::lohko() {
    Vartija vartija(syvyys_);
    tarkista_syvyys();
    odota(Laji::VasenAalto);
    Lauseet tulos;
    while (!on(Laji::OikeaAalto) && !on(Laji::Loppu)) {
        try {
            tulos.push_back(lause());
        } catch (const Jasennysvirhe&) {
            synkronoi();
        }
    }
    odota(Laji::OikeaAalto);
    return tulos;
}
// @loppu lohko

// @alku lause
LauseP Jasennin::lause() {
    Sijainti s = nyt().sijainti;
    switch (nyt().laji) {
    case Laji::Var: {
        kuluta();
        std::string n = odota(Laji::Tunniste, "muuttujan nimeä").teksti;
        odota(Laji::Sijoitus);
        auto arvo = lauseke();
        odota(Laji::Puolipiste);
        return lause(Esittely{n, std::move(arvo)}, s);
    }
// @loppu lause
    case Laji::If:
        return jos();
    case Laji::While: {
        kuluta();
        auto ehto = lauseke();
        return lause(Kun{std::move(ehto), lohko()}, s);
    }
    case Laji::Return: {
        kuluta();
        auto arvo = lauseke();
        odota(Laji::Puolipiste);
        return lause(Palauta{std::move(arvo)}, s);
    }
    case Laji::Print: {
        kuluta();
        odota(Laji::VasenSulku);
        auto arvo = lauseke();
        odota(Laji::OikeaSulku);
        odota(Laji::Puolipiste);
        return lause(Tulosta{std::move(arvo)}, s);
    }
    case Laji::VasenAalto:
        return lause(Lohko{lohko()}, s);
    default:
        break;
    }
// @alku sijoitus
    // Sijoitus tunnistetaan kahden tokenin ennakoinnilla: nimi '='.
    if (on(Laji::Tunniste) && katso(1).laji == Laji::Sijoitus) {
        std::string n = kuluta().teksti;
        kuluta();
        auto arvo = lauseke();
        odota(Laji::Puolipiste);
        return lause(Sijoitus{n, std::move(arvo)}, s);
    }
    auto l = lauseke();
    odota(Laji::Puolipiste);
    return lause(LausekeLause{std::move(l)}, s);
}
// @loppu sijoitus

LauseP Jasennin::jos() {
    Sijainti s = odota(Laji::If).sijainti;
    auto ehto = lauseke();
    Jos tulos{std::move(ehto), lohko(), {}};
    if (vastaa(Laji::Else)) {
        if (on(Laji::If)) {
            tulos.epatosi.push_back(jos());   // else if
        } else {
            tulos.epatosi = lohko();
        }
    }
    return lause(std::move(tulos), s);
}

// @alku pratt
LausekeP Jasennin::lauseke(int minimi) {
    Vartija vartija(syvyys_);
    tarkista_syvyys();
    auto vasen = etuliite();
    for (;;) {
        int voima = sitovuus(nyt().laji);
        if (voima <= minimi) break;    // heikompi operaattori: palataan
        const Tokeni& op = kuluta();
        // Oikea puoli jäsennetään tiukemmalla rajalla, jolloin saman
        // tason operaattorit ryhmittyvät vasemmalle: a - b - c.
        auto oikea = lauseke(voima);
        vasen = uusi(Binaari{op.laji, std::move(vasen), std::move(oikea)},
                     op.sijainti);
    }
    return vasen;
}

LausekeP Jasennin::etuliite() {
    const Tokeni& t = nyt();
    switch (t.laji) {
    case Laji::Luku:
        kuluta();
        return uusi(Luku{t.arvo}, t.sijainti);
    case Laji::True:
    case Laji::False:
        kuluta();
        return uusi(Totuus{t.laji == Laji::True}, t.sijainti);
    case Laji::Miinus:
    case Laji::Ei: {
        kuluta();
        auto a = lauseke(kUnaari);
        return uusi(Unaari{t.laji, std::move(a)}, t.sijainti);
    }
    case Laji::VasenSulku: {
        kuluta();
        auto l = lauseke();
        odota(Laji::OikeaSulku);
        return l;
    }
    case Laji::Tunniste: {
        kuluta();
        if (!vastaa(Laji::VasenSulku)) {
            return uusi(Nimi{t.teksti}, t.sijainti);
        }
        Kutsu k{t.teksti, {}};
        if (!on(Laji::OikeaSulku)) {
            do {
                k.argumentit.push_back(lauseke());
            } while (vastaa(Laji::Pilkku));
        }
        odota(Laji::OikeaSulku);
        return uusi(std::move(k), t.sijainti);
    }
    default:
        virhe("lauseketta");
    }
}
// @loppu pratt

}  // namespace

Ohjelma jasenna(const std::vector<Tokeni>& tokenit, Diagnostiikka& diag) {
    return Jasennin(tokenit, diag).ohjelma();
}

}  // namespace kide
