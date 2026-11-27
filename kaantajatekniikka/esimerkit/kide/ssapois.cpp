#include "ssapois.hpp"

#include <algorithm>
#include <numeric>
#include <set>
#include <utility>

#include "elavyys.hpp"

namespace kide {

namespace {

bool on_phi(const Peruslohko& l) {
    return !l.kaskyt.empty() && l.kaskyt.front().op == Op::Phi;
}

}  // namespace

// @alku kaaret
bool jaa_kriittiset_kaaret(IrFunktio& f) {
    bool muuttui = false;
    std::size_t alkuperaisia = f.lohkot.size();
    for (std::size_t b = 0; b < alkuperaisia; ++b) {
        if (!on_phi(f.lohkot[b]) || f.lohkot[b].edeltajat.size() < 2) {
            continue;
        }
        std::vector<int> edeltajat = f.lohkot[b].edeltajat;
        for (int e : edeltajat) {
            if (f.lohkot[e].seuraajat.size() < 2) continue;
            // Uusi lohko kaarelle e -> b: sen läpi kuljetaan vain tätä
            // kaarta pitkin, joten kopiot eivät näy muilla poluilla.
            int uusi = static_cast<int>(f.lohkot.size());
            f.lohkot.emplace_back();
            f.lohkot[uusi].kaskyt.push_back(
                {.op = Op::Hyppy, .lohkot = {static_cast<int>(b)}});
            for (int& s : f.lohkot[e].kaskyt.back().lohkot) {
                if (s == static_cast<int>(b)) s = uusi;
            }
            for (Kasky& k : f.lohkot[b].kaskyt) {
                if (k.op != Op::Phi) break;
                std::ranges::replace(k.lohkot, e, uusi);
            }
            muuttui = true;
        }
    }
    if (muuttui) laske_reunat(f);
    return muuttui;
}
// @loppu kaaret

namespace {

using Kopio = std::pair<Vreg, Vreg>;         // kohde, lähde

// @alku rinnakkaiset
// Saman lohkon phit lukevat kaikki arvonsa ennen kuin yksikään niistä
// kirjoittaa: kopiot ovat rinnakkaisia. Ne järjestetään niin, ettei
// mikään kopio ylikirjoita arvoa, jota jokin toinen vielä lukee.
std::vector<Kasky> jarjesta_kopiot(std::vector<Kopio> kopiot, IrFunktio& f) {
    std::vector<Kasky> tulos;
    auto kopioi = [&](Vreg kohde, Vreg lahde) {
        tulos.push_back(
            {.op = Op::Kopio, .kohde = kohde, .lahteet = {lahde}});
    };
    std::erase_if(kopiot, [](const Kopio& k) { return k.first == k.second; });
    while (!kopiot.empty()) {
        // Kopion voi tehdä, kun mikään muu ei enää lue sen kohdetta.
        auto vapaa = std::ranges::find_if(kopiot, [&](const Kopio& k) {
            return std::ranges::none_of(kopiot, [&](const Kopio& muu) {
                return muu.second == k.first;
            });
        });
        if (vapaa != kopiot.end()) {
            kopioi(vapaa->first, vapaa->second);
            kopiot.erase(vapaa);
            continue;
        }
        // Jäljellä on vain kiertoja (a <- b, b <- a). Kierto katkaistaan
        // ottamalla yhden kohteen vanha arvo talteen apurekisteriin.
        Vreg kohde = kopiot.front().first;
        f.nimet.push_back("%k" + std::to_string(f.nimet.size()));
        Vreg vara = static_cast<Vreg>(f.nimet.size()) - 1;
        kopioi(vara, kohde);
        for (Kopio& k : kopiot) {
            if (k.second == kohde) k.second = vara;
        }
    }
    return tulos;
}
// @loppu rinnakkaiset

// Naiivi versio: kopiot phien järjestyksessä.
std::vector<Kasky> perakkain(const std::vector<Kopio>& kopiot) {
    std::vector<Kasky> tulos;
    for (const Kopio& k : kopiot) {
        tulos.push_back({.op = Op::Kopio, .kohde = k.first,
                         .lahteet = {k.second}});
    }
    return tulos;
}

}  // namespace

// @alku pura
void pura_phit(IrFunktio& f, Kopiointi tapa) {
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        if (!on_phi(f.lohkot[b])) continue;
        for (int e : f.lohkot[b].edeltajat) {
            std::vector<Kopio> kopiot;
            for (const Kasky& k : f.lohkot[b].kaskyt) {
                if (k.op != Op::Phi) break;
                for (std::size_t i = 0; i < k.lohkot.size(); ++i) {
                    if (k.lohkot[i] == e && k.lahteet[i] >= 0) {
                        kopiot.push_back({k.kohde, k.lahteet[i]});
                    }
                }
            }
            std::vector<Kasky> jono = tapa == Kopiointi::Rinnakkain
                                          ? jarjesta_kopiot(kopiot, f)
                                          : perakkain(kopiot);
            // Kopiot edeltäjän loppuun, ennen sen päättävää hyppyä.
            auto& ks = f.lohkot[e].kaskyt;
            ks.insert(ks.end() - 1, jono.begin(), jono.end());
        }
        std::erase_if(f.lohkot[b].kaskyt,
                      [](const Kasky& k) { return k.op == Op::Phi; });
    }
}
// @loppu pura

// @alku sulauta
bool sulauta_kopiot(IrFunktio& f) {
    std::size_t n = f.nimet.size();
    Elavyys e = laske_elavyys(f);
    // Kaksi rekisteriä häiritsee toisiaan, jos toiseen kirjoitetaan, kun
    // toisen arvoa vielä tarvitaan. Kopio x = y ei tee x:stä ja y:stä
    // häiritseviä, koska niillä on kopion jälkeen sama arvo.
    std::vector<std::set<Vreg>> hairitsee(n);
    auto lisaa = [&](Vreg a, Vreg b) {
        if (a == b) return;
        hairitsee[a].insert(b);
        hairitsee[b].insert(a);
    };
    for (Vreg p = 0; p < f.parametreja; ++p) {
        for (Vreg q = 0; q < p; ++q) lisaa(p, q);
    }
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        std::vector<bool> elava = e.ulos[b];
        const auto& ks = f.lohkot[b].kaskyt;
        for (auto k = ks.rbegin(); k != ks.rend(); ++k) {
            if (k->kohde >= 0) {
                for (std::size_t r = 0; r < n; ++r) {
                    bool kopion_lahde = k->op == Op::Kopio
                        && k->lahteet[0] == static_cast<Vreg>(r);
                    if (elava[r] && !kopion_lahde) {
                        lisaa(k->kohde, static_cast<Vreg>(r));
                    }
                }
                elava[k->kohde] = false;
            }
            for (Vreg r : k->lahteet) {
                if (r >= 0) elava[r] = true;
            }
        }
    }
    // Sulautetut rekisterit muodostavat joukkoja; edustaja on joukon
    // pienin numero, jolloin parametri säilyttää paikkansa.
    std::vector<Vreg> edustaja(n);
    std::iota(edustaja.begin(), edustaja.end(), 0);
    auto etsi = [&](Vreg r) {
        while (edustaja[r] != r) r = edustaja[r];
        return r;
    };
    bool muuttui = false;
    for (const Peruslohko& l : f.lohkot) {
        for (const Kasky& k : l.kaskyt) {
            if (k.op != Op::Kopio) continue;
            Vreg a = etsi(k.kohde), b = etsi(k.lahteet[0]);
            if (a == b || hairitsee[a].count(b)) continue;
            if (a > b) std::swap(a, b);
            edustaja[b] = a;                  // b sulautuu a:han
            // Lähdekoodin muuttujan nimi on väliaikaisen nimeä selkeämpi.
            if (f.nimet[a][0] == '%' || f.nimet[a][0] == '$') {
                f.nimet[a] = f.nimet[b];
            }
            for (Vreg x : hairitsee[b]) {     // ja a perii b:n häiriöt
                hairitsee[x].erase(b);
                lisaa(a, x);
            }
            muuttui = true;
        }
    }
    if (!muuttui) return false;
    for (Peruslohko& l : f.lohkot) {
        for (Kasky& k : l.kaskyt) {
            if (k.kohde >= 0) k.kohde = etsi(k.kohde);
            for (Vreg& r : k.lahteet) {
                if (r >= 0) r = etsi(r);
            }
        }
        std::erase_if(l.kaskyt, [](const Kasky& k) {
            return k.op == Op::Kopio && k.lahteet[0] == k.kohde;
        });
    }
    return true;
}
// @loppu sulauta

void ssa_pois(IrFunktio& f) {
    jaa_kriittiset_kaaret(f);
    pura_phit(f);
    sulauta_kopiot(f);
}

}  // namespace kide
