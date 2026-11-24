// Rajaavien laatikoiden hierarkia (BVH) kolmioille.
#pragma once
#include <algorithm>
#include <vector>

#include "sade.hpp"

// @alku rakenne
// Solmu: laatikko ja joko kaksi lasta (lapsi, lapsi + 1) tai lehti,
// jossa kolmiot jarjestys[eka .. eka + maara).
struct Solmu {
    Laatikko laatikko;
    int eka = 0;      // sisäsolmussa vasen lapsi, lehdessä eka kolmio
    int maara = 0;    // 0 = sisäsolmu
};
struct Bvh {
    std::vector<Solmu> solmut;  // juuri on solmut[0]
    std::vector<int> jarjestys;  // kolmioiden indeksit lehtijärjestyksessä
};
enum class Jako { keskikohta, sah };
// @loppu rakenne

namespace bvh_sisainen {

inline Vec3 keskipiste(const Kolmio& k) {
    return (1.0 / 3) * (k.a + k.b + k.c);
}
inline Laatikko laatikko(const Kolmio& k) {
    Laatikko b;
    laajenna(b, k.a);
    laajenna(b, k.b);
    laajenna(b, k.c);
    return b;
}

// @alku sah
// Pinta-alaheuristiikka (SAH): satunnainen säde osuu laatikkoon
// todennäköisyydellä, joka on verrannollinen pinta-alaan. Jaon hinta
// on C_lapi + P(vasen) N_vasen + P(oikea) N_oikea kolmiotestinä,
// kun laatikkotesti maksaa C_lapi = 1/8 kolmiotestiä. Keskipisteet
// lajitellaan 12 lokeroon akselia kohti.
struct Jakokohta {
    int akseli = -1;
    double raja = 0, hinta = AARETON;
};
inline Jakokohta paras_sah(const std::vector<Kolmio>& kolmiot,
                           const int* idx, int n, const Laatikko& kp,
                           double ala) {
    constexpr int LOKEROT = 12;
    Jakokohta paras;
    for (int a = 0; a < 3; ++a) {
        double lo = akseli(kp.min, a), hi = akseli(kp.max, a);
        if (hi - lo <= 0) continue;
        Laatikko lb[LOKEROT];
        int lm[LOKEROT] = {};
        for (int i = 0; i < n; ++i) {
            const Kolmio& k = kolmiot[idx[i]];
            int j = std::min(LOKEROT - 1, static_cast<int>(
                (akseli(keskipiste(k), a) - lo) / (hi - lo) * LOKEROT));
            ++lm[j];
            laajenna(lb[j], laatikko(k));
        }
        for (int raja = 1; raja < LOKEROT; ++raja) {
            Laatikko v, o;
            int nv = 0, no = 0;
            for (int j = 0; j < LOKEROT; ++j) {
                laajenna(j < raja ? v : o, lb[j]);
                (j < raja ? nv : no) += lm[j];
            }
            if (nv == 0 || no == 0) continue;
            double h = 0.125 +
                       (pinta_ala(v) * nv + pinta_ala(o) * no) / ala;
            if (h < paras.hinta)
                paras = {a, lo + (hi - lo) * raja / LOKEROT, h};
        }
    }
    return paras;
}
// @loppu sah

// @alku rakenna
inline void rakenna(Bvh& b, const std::vector<Kolmio>& kolmiot,
                    int solmu, int eka, int n, Jako jako) {
    Laatikko kaikki, kp;  // kolmioiden ja keskipisteiden laatikot
    for (int i = eka; i < eka + n; ++i) {
        laajenna(kaikki, laatikko(kolmiot[b.jarjestys[i]]));
        laajenna(kp, keskipiste(kolmiot[b.jarjestys[i]]));
    }
    b.solmut[solmu] = {kaikki, eka, n};
    if (n <= 2) return;                       // pieni lehti
    int* alku = b.jarjestys.data() + eka;
    int a;
    double raja;
    if (jako == Jako::sah) {
        Jakokohta j = paras_sah(kolmiot, alku, n, kp, pinta_ala(kaikki));
        // Lehti, jos se on halvempi eikä liian suuri.
        if (j.akseli < 0 || (j.hinta >= n && n <= 8)) return;
        a = j.akseli;
        raja = j.raja;
    } else {
        // Keskikohta: pisin akseli puoliksi keskipisteiden laatikosta.
        Vec3 d = kp.max - kp.min;
        a = d.x >= d.y && d.x >= d.z ? 0 : d.y >= d.z ? 1 : 2;
        raja = (akseli(kp.min, a) + akseli(kp.max, a)) / 2;
        if (akseli(d, a) <= 0) return;        // kaikki samassa kohdassa
    }
    int* keski = std::partition(alku, alku + n, [&](int i) {
        return akseli(keskipiste(kolmiot[i]), a) < raja;
    });
    int nv = static_cast<int>(keski - alku);
    if (nv == 0 || nv == n) return;
    int lapsi = static_cast<int>(b.solmut.size());
    b.solmut.resize(b.solmut.size() + 2);
    b.solmut[solmu].eka = lapsi;
    b.solmut[solmu].maara = 0;
    rakenna(b, kolmiot, lapsi, eka, nv, jako);
    rakenna(b, kolmiot, lapsi + 1, eka + nv, n - nv, jako);
}
// @loppu rakenna

}  // namespace bvh_sisainen

inline Bvh rakenna_bvh(const std::vector<Kolmio>& kolmiot, Jako jako) {
    Bvh b;
    for (int i = 0; i < static_cast<int>(kolmiot.size()); ++i)
        b.jarjestys.push_back(i);
    b.solmut.resize(1);
    bvh_sisainen::rakenna(b, kolmiot, 0, 0,
                          static_cast<int>(kolmiot.size()), jako);
    return b;
}

// @alku lapikaynti
struct BvhLaskuri {
    long laatikot = 0, kolmiot = 0;
};
struct BvhOsuma {
    double t = AARETON;
    int kolmio = -1;
};
// Läpikäynti pinolla. Lapsista lähempi käsitellään ensin, ja solmu
// ohitetaan, jos sen laatikko alkaa kauempana kuin lähin osuma.
inline BvhOsuma leikkaa_bvh(const Bvh& b, const std::vector<Kolmio>& kolmiot,
                            const Sade& s, BvhLaskuri& laskuri) {
    struct Pinossa {
        int solmu;
        double t;  // laatikon alku säteellä
    };
    BvhOsuma o;
    Vec3 kaanteis = kaanteinen(s.d);
    auto testaa = [&](int i) {
        ++laskuri.laatikot;
        return leikkaa_laatikko(b.solmut[i].laatikko, s, kaanteis, 0, o.t);
    };
    Pinossa pino[64];  // syvyys on alle 64 tasoa
    int koko = 0;
    if (double t = testaa(0); t < AARETON) pino[koko++] = {0, t};
    while (koko > 0) {
        Pinossa p = pino[--koko];
        if (p.t >= o.t) continue;
        const Solmu& solmu = b.solmut[p.solmu];
        if (solmu.maara > 0) {
            for (int i = solmu.eka; i < solmu.eka + solmu.maara; ++i) {
                ++laskuri.kolmiot;
                int k = b.jarjestys[i];
                double t = leikkaa_kolmio(kolmiot[k], s, 0, o.t).t;
                if (t < o.t) o = {t, k};
            }
            continue;
        }
        int lahi = solmu.eka, kauka = solmu.eka + 1;
        double tl = testaa(lahi), tk = testaa(kauka);
        if (tk < tl) {
            std::swap(lahi, kauka);
            std::swap(tl, tk);
        }
        if (tk < AARETON) pino[koko++] = {kauka, tk};
        if (tl < AARETON) pino[koko++] = {lahi, tl};
    }
    return o;
}
// @loppu lapikaynti
