// Rajaavien tilavuuksien hierarkia (BVH) akselien suuntaisista
// laatikoista. Rakenne ei tiedä, mitä laatikoiden sisällä on: kohteet
// ovat indeksejä, ja varsinaisen testin tekee kutsuja.
#pragma once
#include "sade.hpp"

#include <numeric>
#include <span>
#include <vector>

// @alku bvh
struct BvhSolmu {
    Laatikko laatikko;
    int vasen = -1, oikea = -1;  // sisäsolmun lapset
    int alku = 0, maara = 0;     // lehden kohteet taulukossa jarjestys
};
struct Bvh {
    std::vector<BvhSolmu> solmut;  // juuri on solmu 0
    std::vector<int> jarjestys;    // kohteiden indeksit lehdittäin
};
struct BvhLaskuri {
    int solmuja = 0, kohteita = 0;  // tehdyt laatikko- ja kohdetestit
};
// @loppu bvh

// @alku rakenna
namespace bvh_apu {
inline double akselilla(Vec3 v, int akseli) {
    return akseli == 0 ? v.x : akseli == 1 ? v.y : v.z;
}
inline int rakenna(Bvh& puu, std::span<const Laatikko> laatikot, int alku,
                   int maara, int lehden_koko) {
    int tama = static_cast<int>(puu.solmut.size());
    puu.solmut.emplace_back();
    Laatikko kaikki = laatikot[puu.jarjestys[alku]];
    for (int i = alku + 1; i < alku + maara; ++i)
        kaikki = yhdiste(kaikki, laatikot[puu.jarjestys[i]]);
    puu.solmut[tama].laatikko = kaikki;
    if (maara <= lehden_koko) {
        puu.solmut[tama].alku = alku;
        puu.solmut[tama].maara = maara;
        return tama;
    }
    // Jako pisimmän akselin suunnassa keskipisteiden mediaanista.
    Vec3 koko = kaikki.max - kaikki.min;
    int akseli = koko.x >= koko.y && koko.x >= koko.z ? 0
                 : koko.y >= koko.z                   ? 1
                                                      : 2;
    auto keski = [&](int i) {
        return akselilla(laatikot[i].min + laatikot[i].max, akseli);
    };
    auto a = puu.jarjestys.begin() + alku;
    std::nth_element(a, a + maara / 2, a + maara, [&](int x, int y) {
        return keski(x) != keski(y) ? keski(x) < keski(y) : x < y;
    });
    int v = rakenna(puu, laatikot, alku, maara / 2, lehden_koko);
    int o = rakenna(puu, laatikot, alku + maara / 2, maara - maara / 2,
                    lehden_koko);
    puu.solmut[tama].vasen = v;
    puu.solmut[tama].oikea = o;
    return tama;
}
}  // namespace bvh_apu

inline Bvh rakenna_bvh(std::span<const Laatikko> laatikot,
                       int lehden_koko = 4) {
    Bvh puu;
    puu.jarjestys.resize(laatikot.size());
    std::iota(puu.jarjestys.begin(), puu.jarjestys.end(), 0);
    if (!laatikot.empty())
        bvh_apu::rakenna(puu, laatikot, 0,
                         static_cast<int>(laatikot.size()), lehden_koko);
    return puu;
}
// @loppu rakenna

// @alku lapikaynti
// Yleinen läpikäynti: haara hylätään kokonaan, jos sen laatikko ei
// kelpaa. Sopii alueen kyselyyn ja näkyvyyskarsintaan.
template <typename Kelpaa, typename Kohde>
void kay_lapi(const Bvh& puu, Kelpaa&& kelpaa, Kohde&& kohde,
              BvhLaskuri* laskuri = nullptr) {
    if (puu.solmut.empty()) return;
    std::vector<int> pino{0};
    while (!pino.empty()) {
        const BvhSolmu& s = puu.solmut[pino.back()];
        pino.pop_back();
        if (laskuri) ++laskuri->solmuja;
        if (!kelpaa(s.laatikko)) continue;
        for (int i = s.alku; i < s.alku + s.maara; ++i) {
            if (laskuri) ++laskuri->kohteita;
            kohde(puu.jarjestys[i]);
        }
        if (s.maara == 0) {
            pino.push_back(s.vasen);
            pino.push_back(s.oikea);
        }
    }
}
// @loppu lapikaynti

// @alku sade-bvh
// Lähin osuma. Haara ohitetaan, jos säde ei osu sen laatikkoon ennen
// jo löydettyä osumaa; testaa(i) tekee tarkan testin kohteelle i.
template <typename Testaa>
Osuma sade_bvh(const Bvh& puu, const Sade& sade, Testaa&& testaa,
               int* kohde = nullptr, BvhLaskuri* laskuri = nullptr) {
    Osuma paras;
    if (puu.solmut.empty()) return paras;
    std::vector<int> pino{0};
    while (!pino.empty()) {
        const BvhSolmu& s = puu.solmut[pino.back()];
        pino.pop_back();
        if (laskuri) ++laskuri->solmuja;
        Osuma l = sade_laatikko(sade, s.laatikko);
        if (!l.osuu || (paras.osuu && l.t > paras.t)) continue;
        for (int i = s.alku; i < s.alku + s.maara; ++i) {
            if (laskuri) ++laskuri->kohteita;
            Osuma o = testaa(puu.jarjestys[i]);
            if (o.osuu && (!paras.osuu || o.t < paras.t)) {
                paras = o;
                if (kohde) *kohde = puu.jarjestys[i];
            }
        }
        if (s.maara == 0) {
            pino.push_back(s.vasen);
            pino.push_back(s.oikea);
        }
    }
    return paras;
}
// @loppu sade-bvh
