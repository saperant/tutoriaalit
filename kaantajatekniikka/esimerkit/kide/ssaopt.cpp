#include "ssaopt.hpp"

#include <algorithm>
#include <map>
#include <optional>
#include <ostream>
#include <set>
#include <stdexcept>
#include <tuple>
#include <utility>

#include "optimointi.hpp"
#include "ssa.hpp"

namespace kide {

namespace {

// Käskyn paikka funktiossa: lohko ja indeksi lohkon sisällä.
struct Paikka {
    int lohko = -1, indeksi = -1;
};

// SSA-muodossa rekisterin nimi yksilöi määrittelynsä, joten
// määrittely–käyttö-ketjut ovat pelkkiä taulukoita.
std::vector<Paikka> maarittelyt(const IrFunktio& f) {
    std::vector<Paikka> m(f.nimet.size());
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        const auto& ks = f.lohkot[b].kaskyt;
        for (std::size_t i = 0; i < ks.size(); ++i) {
            if (ks[i].kohde >= 0) {
                m[ks[i].kohde] = {static_cast<int>(b), static_cast<int>(i)};
            }
        }
    }
    return m;
}

bool dominoi(const std::vector<int>& idom, int a, int b) {
    while (b != a && b != 0) b = idom[b];
    return b == a;
}

}  // namespace

// @alku tarkistin
std::string tarkista_ssa(const IrFunktio& f) {
    std::vector<int> maariteltyja(f.nimet.size(), 0);
    for (Vreg p = 0; p < f.parametreja; ++p) maariteltyja[p] = 1;
    for (const Peruslohko& l : f.lohkot) {
        for (const Kasky& k : l.kaskyt) {
            if (k.kohde >= 0 && ++maariteltyja[k.kohde] > 1) {
                return rekisteri(f, k.kohde) + " määritellään kahdesti";
            }
        }
    }
    std::vector<Paikka> maar = maarittelyt(f);
    std::vector<int> idom = dominoijat(f);
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        if (idom[b] < 0) return "lohkoon L" + std::to_string(b) + " ei pääse";
    }
    // Määrittelyn on dominoitava kohtaa (lohko, indeksi).
    auto nakyy = [&](Vreg r, int lohko, int indeksi) {
        if (r < f.parametreja) return true;
        if (maariteltyja[r] == 0) return false;
        if (maar[r].lohko == lohko) return maar[r].indeksi < indeksi;
        return dominoi(idom, maar[r].lohko, lohko);
    };
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        const Peruslohko& l = f.lohkot[b];
        bool phit_ohi = false;
        for (std::size_t i = 0; i < l.kaskyt.size(); ++i) {
            const Kasky& k = l.kaskyt[i];
            if (paattava(k.op) != (i + 1 == l.kaskyt.size())) {
                return "L" + std::to_string(b) + ": päättävä käsky väärässä"
                       " paikassa";
            }
            if (k.op != Op::Phi) {
                phit_ohi = true;
                for (Vreg r : k.lahteet) {
                    if (r >= 0 && !nakyy(r, static_cast<int>(b),
                                         static_cast<int>(i))) {
                        return rekisteri(f, r) + ": määrittely ei dominoi"
                               " käyttöä lohkossa L" + std::to_string(b);
                    }
                }
                continue;
            }
            if (phit_ohi) return "phi ei ole lohkon alussa";
            std::vector<int> a = k.lohkot, e = l.edeltajat;
            std::ranges::sort(a);
            std::ranges::sort(e);
            if (a != e) {
                return rekisteri(f, k.kohde) + ": phin lohkot eivät vastaa"
                       " edeltäjiä";
            }
            // Phin argumentti luetaan edeltäjän lopussa.
            for (std::size_t j = 0; j < k.lahteet.size(); ++j) {
                int e_koko = static_cast<int>(
                    f.lohkot[k.lohkot[j]].kaskyt.size());
                if (k.lahteet[j] >= 0
                    && !nakyy(k.lahteet[j], k.lohkot[j], e_koko)) {
                    return rekisteri(f, k.lahteet[j]) + ": määrittely ei"
                           " dominoi phin edeltäjää";
                }
            }
        }
    }
    return "";
}
// @loppu tarkistin

// @alku siisti
bool siisti_ssa(IrFunktio& f) {
    bool muuttui = false;
    // 1. Poistetaan lohkot, joihin ei pääse alkulohkosta.
    std::vector<int> uusi(f.lohkot.size(), -1);
    std::vector<int> pino{0};
    uusi[0] = 0;
    while (!pino.empty()) {
        int b = pino.back();
        pino.pop_back();
        const Kasky& viim = f.lohkot[b].kaskyt.back();
        if (viim.op == Op::Palauta) continue;
        for (int s : viim.lohkot) {
            if (uusi[s] < 0) {
                uusi[s] = 0;
                pino.push_back(s);
            }
        }
    }
    std::vector<Peruslohko> lohkot;
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        if (uusi[b] < 0) {
            muuttui = true;
            continue;
        }
        uusi[b] = static_cast<int>(lohkot.size());
        lohkot.push_back(std::move(f.lohkot[b]));
    }
    for (Peruslohko& l : lohkot) {
        for (Kasky& k : l.kaskyt) {
            if (k.op == Op::Palauta) continue;
            // Phin argumentti poistuneesta lohkosta saa numeron -1.
            for (int& s : k.lohkot) s = uusi[s];
        }
    }
    f.lohkot = std::move(lohkot);
    laske_reunat(f);
    // 2. Phiin jäävät vain argumentit, joiden kaari on yhä olemassa.
    for (Peruslohko& l : f.lohkot) {
        for (Kasky& k : l.kaskyt) {
            if (k.op != Op::Phi) break;
            Kasky karsittu{.op = Op::Phi, .kohde = k.kohde};
            for (std::size_t i = 0; i < k.lohkot.size(); ++i) {
                if (std::ranges::count(l.edeltajat, k.lohkot[i]) == 0) {
                    muuttui = true;
                    continue;
                }
                karsittu.lahteet.push_back(k.lahteet[i]);
                karsittu.lohkot.push_back(k.lohkot[i]);
            }
            // Yhden edeltäjän phi on pelkkä kopio.
            if (karsittu.lohkot.size() == 1) {
                karsittu = {.op = Op::Kopio, .kohde = k.kohde,
                            .lahteet = {karsittu.lahteet[0]}};
                muuttui = true;
            }
            k = std::move(karsittu);
        }
    }
    return muuttui;
}
// @loppu siisti

namespace {

// @alku hila
// Rekisterin arvosta tiedetään yksi kolmesta: ei vielä mitään (Yla),
// se on aina sama vakio, tai se ei ole vakio (Ala). Tieto voi vain
// laskea: Yla -> Vakio -> Ala.
struct Arvo {
    enum Taso { Yla, Vakio, Ala } taso = Yla;
    std::int64_t vakio = 0;
    bool operator==(const Arvo&) const = default;
};

// Kahden tiedon yhdistäminen (meet), kun arvo voi tulla kahta reittiä.
Arvo kohtaa(Arvo a, Arvo b) {
    if (a.taso == Arvo::Yla) return b;
    if (b.taso == Arvo::Yla) return a;
    if (a.taso == Arvo::Vakio && a == b) return a;
    return {Arvo::Ala};
}
// @loppu hila

// Harva ehdollinen vakioiden eteneminen (Wegman ja Zadeck 1991).
class VakioidenEteneminen {
public:
    explicit VakioidenEteneminen(IrFunktio& f);
    bool aja();

private:
    Arvo arvo(Vreg r) const { return r < 0 ? Arvo{} : arvot_[r]; }
    void aseta(Vreg r, Arvo a);
    void arvioi(int lohko, const Kasky& k);
    void arvioi_phi(int lohko, const Kasky& k);
    bool kirjoita();

    IrFunktio& f_;
    std::vector<Arvo> arvot_;
    std::vector<std::vector<Paikka>> kayttajat_;   // rekisteri -> käytöt
    std::set<std::pair<int, int>> suoritettavat_;  // kaaret, joita kuljetaan
    std::vector<bool> kayty_;                      // lohkoon päästään
    std::vector<std::pair<int, int>> kaarilista_;
    std::vector<Vreg> arvolista_;
};

VakioidenEteneminen::VakioidenEteneminen(IrFunktio& f)
    : f_(f), arvot_(f.nimet.size()), kayttajat_(f.nimet.size()),
      kayty_(f.lohkot.size()) {
    // Parametrin arvon päättää kutsuja.
    for (Vreg p = 0; p < f.parametreja; ++p) arvot_[p] = {Arvo::Ala};
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        const auto& ks = f.lohkot[b].kaskyt;
        for (std::size_t i = 0; i < ks.size(); ++i) {
            for (Vreg r : ks[i].lahteet) {
                if (r >= 0) {
                    kayttajat_[r].push_back(
                        {static_cast<int>(b), static_cast<int>(i)});
                }
            }
        }
    }
}

// @alku aseta
// Kun rekisterin tieto laskee, sen käyttäjät on arvioitava uudelleen.
void VakioidenEteneminen::aseta(Vreg r, Arvo a) {
    Arvo uusi = kohtaa(arvot_[r], a);
    if (uusi == arvot_[r]) return;
    arvot_[r] = uusi;
    arvolista_.push_back(r);
}

// Phi yhdistää vain ne argumentit, joiden kaarta voidaan kulkea.
void VakioidenEteneminen::arvioi_phi(int lohko, const Kasky& k) {
    Arvo a;
    for (std::size_t i = 0; i < k.lahteet.size(); ++i) {
        if (suoritettavat_.count({k.lohkot[i], lohko})) {
            a = kohtaa(a, arvo(k.lahteet[i]));
        }
    }
    aseta(k.kohde, a);
}
// @loppu aseta

// @alku arvioi
void VakioidenEteneminen::arvioi(int lohko, const Kasky& k) {
    switch (k.op) {
    case Op::Phi: arvioi_phi(lohko, k); return;
    case Op::Vakio: aseta(k.kohde, {Arvo::Vakio, k.vakio}); return;
    case Op::Kopio: aseta(k.kohde, arvo(k.lahteet[0])); return;
    case Op::Kutsu: aseta(k.kohde, {Arvo::Ala}); return;
    case Op::Tulosta:
    case Op::Palauta: return;
    case Op::Hyppy: kaarilista_.push_back({lohko, k.lohkot[0]}); return;
    case Op::Haara: {
        // Tunnettu ehto: vain toinen kaari on suoritettava.
        Arvo ehto = arvo(k.lahteet[0]);
        if (ehto.taso == Arvo::Yla) return;
        if (ehto.taso == Arvo::Ala || ehto.vakio != 0) {
            kaarilista_.push_back({lohko, k.lohkot[0]});
        }
        if (ehto.taso == Arvo::Ala || ehto.vakio == 0) {
            kaarilista_.push_back({lohko, k.lohkot[1]});
        }
        return;
    }
    default: break;
    }
    // Laskutoimitus: vakio, jos kaikki operandit ovat vakioita.
    Arvo a = arvo(k.lahteet[0]);
    Arvo b = k.lahteet.size() > 1 ? arvo(k.lahteet[1])
                                  : Arvo{Arvo::Vakio, 0};
    if (a.taso == Arvo::Ala || b.taso == Arvo::Ala) {
        aseta(k.kohde, {Arvo::Ala});
    } else if (a.taso == Arvo::Vakio && b.taso == Arvo::Vakio) {
        aseta(k.kohde, {Arvo::Vakio, *laskosta(k.op, a.vakio, b.vakio)});
    }
}
// @loppu arvioi

// @alku sccp
bool VakioidenEteneminen::aja() {
    kaarilista_.push_back({-1, 0});          // funktioon tullaan lohkoon L0
    while (!kaarilista_.empty() || !arvolista_.empty()) {
        if (!kaarilista_.empty()) {
            auto [mista, lohko] = kaarilista_.back();
            kaarilista_.pop_back();
            if (!suoritettavat_.insert({mista, lohko}).second) continue;
            const auto& ks = f_.lohkot[lohko].kaskyt;
            // Uusi kaari voi muuttaa phien arvoja; muut käskyt arvioidaan
            // vain, kun lohkoon tullaan ensimmäisen kerran.
            for (const Kasky& k : ks) {
                if (k.op == Op::Phi) arvioi_phi(lohko, k);
            }
            if (kayty_[lohko]) continue;
            kayty_[lohko] = true;
            for (const Kasky& k : ks) {
                if (k.op != Op::Phi) arvioi(lohko, k);
            }
            continue;
        }
        Vreg r = arvolista_.back();
        arvolista_.pop_back();
        for (Paikka p : kayttajat_[r]) {
            if (kayty_[p.lohko]) {
                arvioi(p.lohko, f_.lohkot[p.lohko].kaskyt[p.indeksi]);
            }
        }
    }
    return kirjoita();
}
// @loppu sccp

// @alku kirjoita
// Analyysin tulos kirjoitetaan koodiin: vakioksi todettu määrittely
// korvataan vakiolla ja tunnetun ehdon haara hypyllä.
bool VakioidenEteneminen::kirjoita() {
    bool muuttui = false;
    for (std::size_t b = 0; b < f_.lohkot.size(); ++b) {
        if (!kayty_[b]) continue;             // poistuu siistimisessä
        auto& ks = f_.lohkot[b].kaskyt;
        std::vector<Kasky> phit, muut;
        for (Kasky& k : ks) {
            Arvo a = arvo(k.kohde);
            if (k.kohde >= 0 && a.taso == Arvo::Vakio && k.op != Op::Vakio) {
                k = {.op = Op::Vakio, .kohde = k.kohde, .vakio = a.vakio};
                muuttui = true;
            } else if (Arvo e = arvo(k.op == Op::Haara ? k.lahteet[0] : -1);
                       e.taso == Arvo::Vakio) {
                k = {.op = Op::Hyppy,
                     .lohkot = {k.lohkot[e.vakio != 0 ? 0 : 1]}};
                muuttui = true;
            }
            (k.op == Op::Phi ? phit : muut).push_back(std::move(k));
        }
        // Vakioksi muuttunut phi siirtyy jäljelle jäävien phien perään.
        ks = std::move(phit);
        ks.insert(ks.end(), std::make_move_iterator(muut.begin()),
                  std::make_move_iterator(muut.end()));
    }
    return siisti_ssa(f_) || muuttui;
}
// @loppu kirjoita

// @alku gvn
// Globaali arvonumerointi: dominoivassa lohkossa laskettu lauseke on
// voimassa kaikissa lohkoissa, joita se dominoi. Taulu kulkee
// dominaattoripuuta pitkin syvyyshakuna.
class Arvonumerointi {
public:
    explicit Arvonumerointi(IrFunktio& f)
        : f_(f), edustaja_(f.nimet.size()), vakio_(f.nimet.size()) {
        for (std::size_t r = 0; r < edustaja_.size(); ++r) {
            edustaja_[r] = static_cast<Vreg>(r);
        }
    }
    bool aja();

private:
    using Avain = std::tuple<Op, std::vector<Vreg>, std::int64_t, int>;
    Vreg edustaja(Vreg r) const {
        while (r >= 0 && edustaja_[r] != r) r = edustaja_[r];
        return r;
    }
    void lohko(int b);
    bool phi(Kasky& k, int b);
    void sievenna(Kasky& k) const;
    void nimea_vakio(Vreg r, std::int64_t arvo);

    IrFunktio& f_;
    std::vector<Vreg> edustaja_;                   // sama arvo kuin tässä
    std::vector<std::optional<std::int64_t>> vakio_;
    std::vector<std::vector<int>> lapset_;         // dominaattoripuu
    std::map<Avain, Vreg> taulu_;                  // lauseke -> rekisteri
    bool muuttui_ = false;
};
// @loppu gvn

// @alku gvn-sievenna
// Laskostus ja samat algebralliset säännöt kuin luvun 11 passissa. Erona
// on, että vakio tunnetaan, vaikka se olisi määritelty toisessa lohkossa.
void Arvonumerointi::sievenna(Kasky& k) const {
    auto vakio = [&](std::size_t i) -> std::optional<std::int64_t> {
        if (i >= k.lahteet.size() || k.lahteet[i] < 0) return std::nullopt;
        return vakio_[k.lahteet[i]];
    };
    auto a = vakio(0);
    auto b = vakio(1);
    Vreg x = k.lahteet[0];
    Vreg y = k.lahteet.size() > 1 ? k.lahteet[1] : -1;
    auto vakioksi = [&](std::int64_t arvo) {
        k = {.op = Op::Vakio, .kohde = k.kohde, .vakio = arvo};
    };
    auto kopioksi = [&](Vreg lahde) {
        k = {.op = Op::Kopio, .kohde = k.kohde, .lahteet = {lahde}};
    };
    if (a && (y < 0 || b)) {
        vakioksi(*laskosta(k.op, *a, b.value_or(0)));
    } else if ((k.op == Op::Add || k.op == Op::Sub) && b == 0) {
        kopioksi(x);
    } else if (k.op == Op::Add && a == 0) {
        kopioksi(y);
    } else if (k.op == Op::Mul && (a == 0 || b == 0)) {
        vakioksi(0);
    } else if (k.op == Op::Mul && b == 1) {
        kopioksi(x);
    } else if (k.op == Op::Mul && a == 1) {
        kopioksi(y);
    }
}
// @loppu gvn-sievenna

// Vakion edustaja edustaa kaikkia saman vakion määrittelyjä, joita se
// dominoi. Tulosteiden luettavuuden vuoksi se nimetään arvonsa mukaan
// ($0, $1, ...), jos nimi on vapaa.
void Arvonumerointi::nimea_vakio(Vreg r, std::int64_t arvo) {
    vakio_[r] = arvo;
    std::string nimi = "$" + std::to_string(arvo);
    if (std::ranges::count(f_.nimet, nimi) == 0) f_.nimet[r] = nimi;
}

// Phi on tarpeeton, jos kaikki sen argumentit ovat sama arvo (tai phi
// itse). Palauttaa true, jos phi poistetaan.
bool Arvonumerointi::phi(Kasky& k, int b) {
    Vreg sama = -1;
    bool yksi = true;
    for (Vreg& r : k.lahteet) {
        r = edustaja(r);
        if (r == k.kohde) continue;
        if (r < 0 || (sama >= 0 && r != sama)) yksi = false;
        sama = r;
    }
    if (yksi && sama >= 0) {
        edustaja_[k.kohde] = sama;
        return true;
    }
    // Kaksi phitä samoilla argumenteilla samassa lohkossa on sama arvo.
    Avain avain{Op::Phi, k.lahteet, 0, b};
    if (auto t = taulu_.find(avain); t != taulu_.end()) {
        edustaja_[k.kohde] = t->second;
        return true;
    }
    taulu_[avain] = k.kohde;
    return false;
}

// @alku gvn-lohko
void Arvonumerointi::lohko(int b) {
    std::vector<Avain> lisatyt;
    std::vector<Kasky> pidetaan;
    for (Kasky& k : f_.lohkot[b].kaskyt) {
        if (k.op == Op::Phi) {
            if (phi(k, b)) {
                muuttui_ = true;
            } else {
                lisatyt.push_back({Op::Phi, k.lahteet, 0, b});
                pidetaan.push_back(std::move(k));
            }
            continue;
        }
        for (Vreg& r : k.lahteet) r = edustaja(r);
        if (puhdas(k.op) && k.op != Op::Vakio && k.op != Op::Kopio) {
            Op ennen = k.op;
            sievenna(k);
            muuttui_ |= k.op != ennen;
            if (vaihdannainen(k.op) && k.lahteet[0] > k.lahteet[1]) {
                std::swap(k.lahteet[0], k.lahteet[1]);
            }
        }
        // Kopio ei laske mitään: kohteella on sama arvo kuin lähteellä.
        if (k.op == Op::Kopio) {
            edustaja_[k.kohde] = k.lahteet[0];
            muuttui_ = true;
            continue;
        }
        if (puhdas(k.op)) {
            Avain avain{k.op, k.lahteet, k.vakio, -1};
            if (auto t = taulu_.find(avain); t != taulu_.end()) {
                edustaja_[k.kohde] = t->second;   // laskettu jo aiemmin
                muuttui_ = true;
                continue;
            }
            taulu_[avain] = k.kohde;
            lisatyt.push_back(std::move(avain));
            if (k.op == Op::Vakio) nimea_vakio(k.kohde, k.vakio);
        }
        pidetaan.push_back(std::move(k));
    }
    f_.lohkot[b].kaskyt = std::move(pidetaan);
    for (int lapsi : lapset_[b]) lohko(lapsi);
    // Tämän lohkon lausekkeet eivät näy sisarlohkoissa.
    for (const Avain& a : lisatyt) taulu_.erase(a);
}
// @loppu gvn-lohko

bool Arvonumerointi::aja() {
    std::vector<int> idom = dominoijat(f_);
    lapset_.assign(f_.lohkot.size(), {});
    for (std::size_t b = 1; b < f_.lohkot.size(); ++b) {
        lapset_[idom[b]].push_back(static_cast<int>(b));
    }
    lohko(0);
    // Paluukaarten phi-argumentit ja muut jo ohitetut käytöt.
    for (Peruslohko& l : f_.lohkot) {
        for (Kasky& k : l.kaskyt) {
            for (Vreg& r : k.lahteet) r = edustaja(r);
        }
    }
    return muuttui_;
}

}  // namespace

bool etene_vakiot(IrFunktio& f) { return VakioidenEteneminen(f).aja(); }

bool numeroi_arvot_ssa(IrFunktio& f) { return Arvonumerointi(f).aja(); }

// @alku kuollut-ssa
// Merkitse ja lakaise: elävää on se, millä on sivuvaikutus tai mikä
// ohjaa suoritusta, ja kaikki, mitä elävä käsky lukee.
bool poista_kuollut_ssa(IrFunktio& f) {
    std::vector<Paikka> maar = maarittelyt(f);
    std::vector<std::vector<bool>> elava(f.lohkot.size());
    std::vector<Paikka> tyolista;
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        const auto& ks = f.lohkot[b].kaskyt;
        elava[b].assign(ks.size(), false);
        for (std::size_t i = 0; i < ks.size(); ++i) {
            if (!puhdas(ks[i].op)) {
                elava[b][i] = true;
                tyolista.push_back({static_cast<int>(b),
                                    static_cast<int>(i)});
            }
        }
    }
    while (!tyolista.empty()) {
        Paikka p = tyolista.back();
        tyolista.pop_back();
        for (Vreg r : f.lohkot[p.lohko].kaskyt[p.indeksi].lahteet) {
            if (r < 0 || maar[r].lohko < 0) continue;      // parametri
            Paikka m = maar[r];
            if (!elava[m.lohko][m.indeksi]) {
                elava[m.lohko][m.indeksi] = true;
                tyolista.push_back(m);
            }
        }
    }
    bool muuttui = false;
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        auto& ks = f.lohkot[b].kaskyt;
        std::vector<Kasky> pidetaan;
        for (std::size_t i = 0; i < ks.size(); ++i) {
            if (elava[b][i]) pidetaan.push_back(std::move(ks[i]));
        }
        muuttui |= pidetaan.size() != ks.size();
        ks = std::move(pidetaan);
    }
    return muuttui;
}
// @loppu kuollut-ssa

// @alku optimoi-ssa
void optimoi_ssa(IrFunktio& f, std::ostream* loki) {
    struct Passi {
        const char* nimi;
        bool (*aja)(IrFunktio&);
    };
    const Passi passit[] = {
        {"vakioiden eteneminen", etene_vakiot},
        {"globaali arvonumerointi", numeroi_arvot_ssa},
        {"kuollut koodi", poista_kuollut_ssa},
    };
    for (bool muuttui = true; muuttui;) {
        muuttui = false;
        for (const Passi& p : passit) {
            if (!p.aja(f)) continue;
            muuttui = true;
            // Jokaisen passin on jätettävä funktio SSA-muotoon.
            if (std::string virhe = tarkista_ssa(f); !virhe.empty()) {
                throw std::logic_error(std::string("passi '") + p.nimi
                                       + "' rikkoi SSA-muodon: " + virhe);
            }
            if (loki) {
                *loki << "; passin '" << p.nimi << "' jälkeen\n";
                tulosta_ir(f, *loki);
            }
        }
    }
}
// @loppu optimoi-ssa

}  // namespace kide
