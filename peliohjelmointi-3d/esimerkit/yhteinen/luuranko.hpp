// Luurankoanimaatio: nivelhierarkia, sidontapoosi, skinnaus,
// animaatioleikkeen näytteistys ja poosien sekoitus.
#pragma once
#include "kvaternio.hpp"

#include <algorithm>
#include <string>
#include <vector>

// @alku luuranko
struct Nivel {
    std::string nimi;
    int vanhempi = -1;  // vanhempi on taulukossa ennen lasta
    Muunnos lepo;       // paikallinen muunnos sidontapoosissa
    Mat4 kaanteinen_sidonta = yksikko();
};
struct Luuranko {
    std::vector<Nivel> nivelet;
};
// Poosi on yksi paikallinen muunnos jokaiselle nivelelle.
using Poosi = std::vector<Muunnos>;

inline Poosi lepopoosi(const Luuranko& l) {
    Poosi p;
    for (const Nivel& n : l.nivelet) p.push_back(n.lepo);
    return p;
}
// Nivelten matriisit mallin koordinaatistossa: sama läpikäynti kuin
// näkymäpuussa.
inline std::vector<Mat4> nivelmatriisit(const Luuranko& l, const Poosi& p) {
    std::vector<Mat4> m(l.nivelet.size());
    for (std::size_t i = 0; i < m.size(); ++i) {
        int v = l.nivelet[i].vanhempi;
        m[i] = v >= 0 ? m[v] * matriisi(p[i]) : matriisi(p[i]);
    }
    return m;
}
// @loppu luuranko

// @alku sidonta
// Käänteinen sidontamatriisi vie mallin pisteen nivelen omaan
// koordinaatistoon sellaisena kuin nivel oli, kun verkko sidottiin.
inline void laske_sidonta(Luuranko& l) {
    std::vector<Mat4> m = nivelmatriisit(l, lepopoosi(l));
    for (std::size_t i = 0; i < m.size(); ++i)
        l.nivelet[i].kaanteinen_sidonta = kaanteinen(m[i]);
}
// Skinnausmatriisi: ensin sidontapoosista nivelen koordinaatistoon,
// sitten nivelen nykyisen asennon mukana takaisin malliin.
inline std::vector<Mat4> skinnausmatriisit(const Luuranko& l,
                                           const Poosi& p) {
    std::vector<Mat4> m = nivelmatriisit(l, p);
    for (std::size_t i = 0; i < m.size(); ++i)
        m[i] = m[i] * l.nivelet[i].kaanteinen_sidonta;
    return m;
}
// @loppu sidonta

// @alku skinnaus
// Verteksi seuraa enintään neljää niveltä; painojen summa on 1.
struct Painot {
    int nivel[4] = {0, 0, 0, 0};
    double paino[4] = {1, 0, 0, 0};
};
// Lineaarinen sekoitusskinnaus: verteksi muunnetaan jokaisen nivelen
// matriisilla ja tulokset lasketaan yhteen painotettuina.
inline Vec3 skinnaa(Vec3 p, const Painot& w, const std::vector<Mat4>& m) {
    Vec3 tulos;
    for (int k = 0; k < 4; ++k)
        if (w.paino[k] > 0)
            tulos = tulos + w.paino[k] * muunna_piste(m[w.nivel[k]], p);
    return tulos;
}
// @loppu skinnaus

// @alku leike
// Kanava animoi yhden nivelen yhtä ominaisuutta avainkehyksillä.
struct Kanava {
    enum class Kohde { Siirto, Kierto, Skaala };
    int nivel = 0;
    Kohde kohde = Kohde::Kierto;
    std::vector<double> ajat;     // nousevassa järjestyksessä
    std::vector<Vec3> vektorit;   // siirron ja skaalan arvot
    std::vector<Kvat> kierrot;    // kierron arvot
};
struct Leike {
    std::string nimi;
    double kesto = 0;
    std::vector<Kanava> kanavat;
};
// @loppu leike

// @alku nayte
// Leikkeen poosi hetkellä t. Aika kiertää leikkeen alusta, ja arvo
// interpoloidaan kahden ympäröivän avainkehyksen väliltä.
inline Poosi nayte(const Leike& leike, const Luuranko& l, double t) {
    Poosi p = lepopoosi(l);
    t = std::fmod(t, leike.kesto);
    for (const Kanava& k : leike.kanavat) {
        auto seuraava = std::upper_bound(k.ajat.begin(), k.ajat.end(), t);
        std::size_t b = std::min<std::size_t>(seuraava - k.ajat.begin(),
                                              k.ajat.size() - 1);
        std::size_t a = b > 0 ? b - 1 : 0;
        double vali = k.ajat[b] - k.ajat[a];
        double u = vali > 0 ? std::clamp((t - k.ajat[a]) / vali, 0.0, 1.0)
                            : 0.0;
        Muunnos& m = p[k.nivel];
        if (k.kohde == Kanava::Kohde::Kierto)
            m.kierto = slerp(k.kierrot[a], k.kierrot[b], u);
        else if (k.kohde == Kanava::Kohde::Siirto)
            m.sijainti = lerp(k.vektorit[a], k.vektorit[b], u);
        else
            m.skaala = lerp(k.vektorit[a], k.vektorit[b], u);
    }
    return p;
}
// @loppu nayte

// @alku sekoitus
// Kahden poosin sekoitus nivel kerrallaan: paino 0 antaa a:n, 1 b:n.
inline Poosi sekoita(const Poosi& a, const Poosi& b, double paino) {
    Poosi p(a.size());
    for (std::size_t i = 0; i < a.size(); ++i)
        p[i] = sekoita(a[i], b[i], paino);
    return p;
}
// @loppu sekoitus
