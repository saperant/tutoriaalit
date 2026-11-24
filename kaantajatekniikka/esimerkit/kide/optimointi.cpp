#include "optimointi.hpp"

#include <algorithm>
#include <optional>
#include <ostream>
#include <unordered_map>

#include "elavyys.hpp"
#include "semantiikka.hpp"

namespace kide {

// @alku saavuttamattomat
bool poista_saavuttamattomat(IrFunktio& f) {
    std::vector<int> uusi(f.lohkot.size(), -1);
    std::vector<int> pino{0}, jarjestys;
    uusi[0] = 0;
    while (!pino.empty()) {            // syvyyshaku alkulohkosta
        int b = pino.back();
        pino.pop_back();
        jarjestys.push_back(b);
        const Kasky& viim = f.lohkot[b].kaskyt.back();
        if (viim.op == Op::Palauta) continue;
        for (int s : viim.lohkot) {
            if (uusi[s] < 0) {
                uusi[s] = 0;
                pino.push_back(s);
            }
        }
    }
    if (jarjestys.size() == f.lohkot.size()) return false;
    std::sort(jarjestys.begin(), jarjestys.end());   // säilytä järjestys
    std::vector<Peruslohko> lohkot;
    for (int b : jarjestys) {
        uusi[b] = static_cast<int>(lohkot.size());
        lohkot.push_back(std::move(f.lohkot[b]));
    }
    for (Peruslohko& l : lohkot) {
        if (l.kaskyt.back().op == Op::Palauta) continue;
        for (int& s : l.kaskyt.back().lohkot) s = uusi[s];
    }
    f.lohkot = std::move(lohkot);
    laske_reunat(f);
    return true;
}
// @loppu saavuttamattomat

namespace {

namespace s = semantiikka;

// @alku laskostus
// Laskee käännösaikana operaation, jonka kaikki operandit tunnetaan.
// Samat funktiot kuin tulkissa: optimointi ei muuta ohjelman merkitystä.
std::optional<std::int64_t> laskosta(Op op, std::int64_t a, std::int64_t b) {
    switch (op) {
    case Op::Neg: return s::vastaluku(a);
    case Op::Not: return a == 0;
    case Op::Add: return s::summa(a, b);
    case Op::Sub: return s::erotus(a, b);
    case Op::Mul: return s::tulo(a, b);
    case Op::Div: return s::osamaara(a, b);
    case Op::Rem: return s::jakojaannos(a, b);
    case Op::Eq: return a == b;
    case Op::Ne: return a != b;
    case Op::Lt: return a < b;
    case Op::Le: return a <= b;
    case Op::Gt: return a > b;
    case Op::Ge: return a >= b;
    default: return std::nullopt;
    }
}
// @loppu laskostus

bool vaihdannainen(Op op) {
    return op == Op::Add || op == Op::Mul || op == Op::Eq || op == Op::Ne;
}

// @alku numerointi
// Paikallinen arvonumerointi yhden peruslohkon sisällä. Pidetään kirjaa
// siitä, mitä kunkin rekisterin arvosta tiedetään juuri tällä kohtaa.
class Numerointi {
public:
    bool lohko(Peruslohko& b);

private:
    struct Lauseke {             // laskettu arvo ja sen rekisteri
        Op op;
        std::vector<Vreg> lahteet;
        std::int64_t vakio;
        Vreg rekisteri;
    };
    void unohda(Vreg r);         // r kirjoitetaan: tieto vanhenee
    void muista(const Kasky& k);
    bool sievenna(Kasky& k);

    std::unordered_map<Vreg, std::int64_t> vakiot_;
    std::unordered_map<Vreg, Vreg> kopiot_;   // r on kopio rekisteristä
    std::vector<Lauseke> lausekkeet_;
};

void Numerointi::unohda(Vreg r) {
    vakiot_.erase(r);
    std::erase_if(kopiot_, [r](const auto& p) {
        return p.first == r || p.second == r;
    });
    std::erase_if(lausekkeet_, [r](const Lauseke& l) {
        return l.rekisteri == r || std::ranges::count(l.lahteet, r) > 0;
    });
}

void Numerointi::muista(const Kasky& k) {
    if (k.op == Op::Vakio) vakiot_[k.kohde] = k.vakio;
    if (k.op == Op::Kopio) {
        if (k.lahteet[0] != k.kohde) kopiot_[k.kohde] = k.lahteet[0];
        return;
    }
    if (!puhdas(k.op) || k.op == Op::Vakio
        || std::ranges::count(k.lahteet, k.kohde) > 0) {
        return;
    }
    lausekkeet_.push_back({k.op, k.lahteet, k.vakio, k.kohde});
}
// @loppu numerointi

// Sieventää käskyn tunnetun tiedon perusteella. Palauttaa true, jos
// käsky muuttui.
bool Numerointi::sievenna(Kasky& k) {
    bool muuttui = false;
    for (Vreg& r : k.lahteet) {                   // kopioiden eteneminen
        if (auto c = kopiot_.find(r); c != kopiot_.end()) {
            r = c->second;
            muuttui = true;
        }
    }
    auto vakio = [&](std::size_t i) -> std::optional<std::int64_t> {
        if (i >= k.lahteet.size()) return std::nullopt;
        auto v = vakiot_.find(k.lahteet[i]);
        if (v == vakiot_.end()) return std::nullopt;
        return v->second;
    };
    auto korvaa_vakiolla = [&](std::int64_t arvo) {
        k = {.op = Op::Vakio, .kohde = k.kohde, .vakio = arvo};
        return true;
    };
    auto korvaa_kopiolla = [&](Vreg lahde) {
        k = {.op = Op::Kopio, .kohde = k.kohde, .lahteet = {lahde}};
        return true;
    };
    if (k.op == Op::Haara) {                      // tunnettu ehto
        if (auto c = vakio(0)) {
            int kohde = *c ? k.lohkot[0] : k.lohkot[1];
            k = {.op = Op::Hyppy, .lohkot = {kohde}};
            return true;
        }
        return muuttui;
    }
    if (k.op == Op::Kopio) {
        if (auto c = vakio(0)) return korvaa_vakiolla(*c);
        return muuttui;
    }
    // @alku sievenna
    if (!puhdas(k.op) || k.op == Op::Vakio) return muuttui;
    auto a = vakio(0);
    auto b = vakio(1);
    if (a && (k.lahteet.size() == 1 || b)) {      // vakioiden laskostus
        if (auto t = laskosta(k.op, *a, b.value_or(0))) {
            return korvaa_vakiolla(*t);
        }
    }
    // Algebralliset sievennykset: x + 0, x - 0, x * 1 ja x * 0.
    if ((k.op == Op::Add || k.op == Op::Sub) && b == 0) {
        return korvaa_kopiolla(k.lahteet[0]);
    }
    if (k.op == Op::Add && a == 0) return korvaa_kopiolla(k.lahteet[1]);
    if (k.op == Op::Mul && (a == 0 || b == 0)) return korvaa_vakiolla(0);
    if (k.op == Op::Mul && b == 1) return korvaa_kopiolla(k.lahteet[0]);
    if (k.op == Op::Mul && a == 1) return korvaa_kopiolla(k.lahteet[1]);
    // Yhteiset alilausekkeet: sama operaatio samoille arvoille.
    if (vaihdannainen(k.op) && k.lahteet[0] > k.lahteet[1]) {
        std::swap(k.lahteet[0], k.lahteet[1]);
    }
    for (const Lauseke& l : lausekkeet_) {
        if (l.op == k.op && l.lahteet == k.lahteet && l.vakio == k.vakio) {
            return korvaa_kopiolla(l.rekisteri);
        }
    }
    return muuttui;
}
// @loppu sievenna

bool Numerointi::lohko(Peruslohko& b) {
    bool muuttui = false;
    for (Kasky& k : b.kaskyt) {
        muuttui |= sievenna(k);
        if (k.kohde >= 0) {
            unohda(k.kohde);
            muista(k);
        }
    }
    // Kopio itseensä (x = x) on tarpeeton.
    muuttui |= std::erase_if(b.kaskyt, [](const Kasky& k) {
        return k.op == Op::Kopio && k.lahteet[0] == k.kohde;
    }) > 0;
    return muuttui;
}

}  // namespace

bool numeroi_arvot(IrFunktio& f) {
    bool muuttui = false;
    for (Peruslohko& b : f.lohkot) muuttui |= Numerointi().lohko(b);
    if (muuttui) laske_reunat(f);
    return muuttui;
}

// @alku ohjausvuo
bool siisti_ohjausvuo(IrFunktio& f) {
    bool muuttui = false;
    // 1. Hyppy tyhjään lohkoon, joka vain hyppää eteenpäin, ohjataan
    //    suoraan perille.
    auto perille = [&](int b) {
        for (std::size_t askel = 0; askel < f.lohkot.size(); ++askel) {
            const auto& k = f.lohkot[b].kaskyt;
            if (b == 0 || k.size() != 1 || k[0].op != Op::Hyppy) break;
            b = k[0].lohkot[0];
        }
        return b;
    };
    for (Peruslohko& l : f.lohkot) {
        Kasky& viim = l.kaskyt.back();
        if (viim.op == Op::Palauta) continue;
        for (int& s : viim.lohkot) {
            int p = perille(s);
            muuttui |= p != s;
            s = p;
        }
        if (viim.op == Op::Haara && viim.lohkot[0] == viim.lohkot[1]) {
            viim = {.op = Op::Hyppy, .lohkot = {viim.lohkot[0]}};
            muuttui = true;
        }
    }
    laske_reunat(f);
    // 2. Lohko, jolla on ainoa seuraaja, jonka ainoa edeltäjä se on,
    //    yhdistetään seuraajaansa.
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        for (;;) {
            Peruslohko& l = f.lohkot[b];
            if (l.kaskyt.back().op != Op::Hyppy) break;
            int s = l.kaskyt.back().lohkot[0];
            if (s == 0 || s == static_cast<int>(b)
                || f.lohkot[s].edeltajat.size() != 1) {
                break;
            }
            l.kaskyt.pop_back();
            auto& sk = f.lohkot[s].kaskyt;
            l.kaskyt.insert(l.kaskyt.end(), sk.begin(), sk.end());
            // Seuraaja jää ilman edeltäjiä; se poistetaan alempana.
            sk = {{.op = Op::Hyppy, .lohkot = {s}}};
            laske_reunat(f);
            muuttui = true;
        }
    }
    return poista_saavuttamattomat(f) || muuttui;
}
// @loppu ohjausvuo

// @alku kuollut
bool poista_kuollut_koodi(IrFunktio& f) {
    Elavyys e = laske_elavyys(f);
    bool muuttui = false;
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        std::vector<bool> elava = e.ulos[b];
        auto& kaskyt = f.lohkot[b].kaskyt;
        std::vector<Kasky> pidetaan;
        for (auto k = kaskyt.rbegin(); k != kaskyt.rend(); ++k) {
            if (k->kohde >= 0 && puhdas(k->op) && !elava[k->kohde]) {
                muuttui = true;            // tulosta ei lueta koskaan
                continue;
            }
            if (k->kohde >= 0) elava[k->kohde] = false;
            for (Vreg r : k->lahteet) elava[r] = true;
            pidetaan.push_back(std::move(*k));
        }
        std::reverse(pidetaan.begin(), pidetaan.end());
        kaskyt = std::move(pidetaan);
    }
    return muuttui;
}
// @loppu kuollut

// @alku kopiot
bool yhdista_kopiot(IrFunktio& f) {
    Elavyys e = laske_elavyys(f);
    bool muuttui = false;
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        auto& ks = f.lohkot[b].kaskyt;
        // elavat[i]: rekisterit, joita luetaan käskyn i jälkeen.
        std::vector<std::vector<bool>> elavat(ks.size());
        std::vector<bool> elava = e.ulos[b];
        for (std::size_t i = ks.size(); i-- > 0;) {
            elavat[i] = elava;
            if (ks[i].kohde >= 0) elava[ks[i].kohde] = false;
            for (Vreg r : ks[i].lahteet) elava[r] = true;
        }
        for (std::size_t i = 0; i + 1 < ks.size(); ++i) {
            Kasky& laskenta = ks[i];
            const Kasky& kopio = ks[i + 1];
            Vreg t = laskenta.kohde;
            if (kopio.op == Op::Kopio && t >= 0 && kopio.lahteet[0] == t
                && kopio.kohde != t && !elavat[i + 1][t]) {
                laskenta.kohde = kopio.kohde;   // kirjoitetaan suoraan
                ks.erase(ks.begin() + static_cast<std::ptrdiff_t>(i) + 1);
                muuttui = true;
                break;     // elävyystieto vanheni; jatketaan seuraavalla
            }              // optimointikierroksella
        }
    }
    return muuttui;
}
// @loppu kopiot

// @alku optimoi
void optimoi(IrFunktio& f, std::ostream* loki) {
    struct Passi {
        const char* nimi;
        bool (*aja)(IrFunktio&);
    };
    const Passi passit[] = {
        {"saavuttamattomat lohkot", poista_saavuttamattomat},
        {"arvonumerointi", numeroi_arvot},
        {"ohjausvuon siistiminen", siisti_ohjausvuo},
        {"kuollut koodi", poista_kuollut_koodi},
        {"kopioiden yhdistäminen", yhdista_kopiot},
    };
    for (bool muuttui = true; muuttui;) {
        muuttui = false;
        for (const Passi& p : passit) {
            if (!p.aja(f)) continue;
            muuttui = true;
            if (loki) {
                *loki << "; passin '" << p.nimi << "' jälkeen\n";
                tulosta_ir(f, *loki);
            }
        }
    }
}
// @loppu optimoi

}  // namespace kide
