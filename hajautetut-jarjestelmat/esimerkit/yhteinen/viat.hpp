// Satunnaiset vikaohjelmat: solmujen kaatumisia ja verkon jakoja,
// jotka arvotaan siemenestä ja asennetaan simulaattoriin.
#pragma once
#include <algorithm>
#include <string>
#include <vector>

#include "satunnainen.hpp"
#include "simulaattori.hpp"

// @alku vika
struct Vika {
    enum class Laji { Kaatuminen, Jako } laji;
    Aika alku, kesto;
    int solmu;                 // kaatuva solmu tai jaon pienempi puoli
    std::vector<int> ryhma;    // jaon toinen puoli
};

inline std::string kuvaus(const Vika& v) {
    std::string s = std::to_string(v.alku) + "-" +
                    std::to_string(v.alku + v.kesto) + " ms: ";
    if (v.laji == Vika::Laji::Kaatuminen)
        return s + "solmu " + std::to_string(v.solmu) + " kaatuu";
    s += "jako {";
    for (size_t i = 0; i < v.ryhma.size(); ++i)
        s += (i ? "," : "") + std::to_string(v.ryhma[i]);
    return s + "} | muut";
}

// Arpoo `maara` vikaa väliltä [100, kesto]. Jako erottaa satunnaisen
// osajoukon muista solmuista.
inline std::vector<Vika> arvo_viat(std::uint64_t siemen, int solmuja,
                                   int maara, Aika kesto) {
    Satunnainen r(siemen, 7);
    std::vector<Vika> viat;
    for (int i = 0; i < maara; ++i) {
        Vika v{.laji = r.tapahtuu(500) ? Vika::Laji::Kaatuminen
                                       : Vika::Laji::Jako,
               .alku = r.valilta(100, kesto), .kesto = r.valilta(50, 800),
               .solmu = static_cast<int>(r.valilta(0, solmuja - 1)),
               .ryhma = {}};
        if (v.laji == Vika::Laji::Jako) {
            int koko = static_cast<int>(r.valilta(1, solmuja / 2));
            for (int s = 0; s < solmuja && koko > 0; ++s)
                if (s == v.solmu || r.tapahtuu(400)) {
                    v.ryhma.push_back(s);
                    --koko;
                }
        }
        viat.push_back(std::move(v));
    }
    std::stable_sort(viat.begin(), viat.end(),
                     [](const Vika& a, const Vika& b) {
                         return a.alku < b.alku;
                     });
    return viat;
}
// @loppu vika

// @alku asenna
// Kaatunut solmu käynnistyy keston jälkeen uudelleen; jako korjataan
// keston jälkeen. Päällekkäiset jaot korvaavat toisensa.
template <class S>
void asenna(S& sim, const std::vector<Vika>& viat) {
    for (const Vika& v : viat) {
        if (v.laji == Vika::Laji::Kaatuminen) {
            sim.kun(v.alku, [&sim, s = v.solmu] { sim.kaada(s); });
            sim.kun(v.alku + v.kesto, [&sim, s = v.solmu] {
                sim.kaynnista(s);
            });
        } else {
            sim.kun(v.alku, [&sim, r = v.ryhma] { sim.jaa({r}); });
            sim.kun(v.alku + v.kesto, [&sim] { sim.paranna(); });
        }
    }
}
// @loppu asenna
