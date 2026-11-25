// Kapea vaihe: kosketuspisteet kahden kappaleen välille. Normaali
// osoittaa aina kappaleesta a kappaleeseen b.
#pragma once
#include "kappale.hpp"

#include <algorithm>
#include <array>
#include <utility>
#include <vector>

// @alku monisto
// Kosketus luodaan jo, kun pintojen väli on tätä pienempi. Silloin
// syvyys on negatiivinen, ja ratkaisija sallii lähestymisen vain raon
// verran (ennakoiva kosketus). Lepäävän kappaleen pisteet eivät välky
// pois ja takaisin laskentatarkkuuden rajalla.
inline constexpr double MARGINAALI = 0.01;

struct Kosketuspiste {
    Vec3 piste;         // maailmassa
    double syvyys = 0;  // tunkeuma normaalin suunnassa; rako < 0
    // Ratkaisijan muisti (luku 7): kertyneet impulssit normaalin ja
    // kahden tangentin suunnassa.
    double jn = 0, jt1 = 0, jt2 = 0;
};
// Monisto (contact manifold): kahden kappaleen kaikki kosketuspisteet
// ja niiden yhteinen normaali.
struct Monisto {
    int a = 0, b = 0;  // kappaleiden indeksit
    Vec3 normaali;     // a:sta b:hen
    std::vector<Kosketuspiste> pisteet;
};
// @loppu monisto

// @alku pallot
inline void pallo_pallo(const Kappale& a, const Kappale& b, Monisto& m) {
    Vec3 d = b.sijainti - a.sijainti;
    double etaisyys = pituus(d), summa = a.muoto.sade + b.muoto.sade;
    if (etaisyys >= summa + MARGINAALI) return;
    // Sisäkkäisille keskipisteille mikä tahansa suunta kelpaa.
    m.normaali = etaisyys > 1e-9 ? (1 / etaisyys) * d : Vec3{0, 1, 0};
    m.pisteet.push_back(
        {a.sijainti + a.muoto.sade * m.normaali, summa - etaisyys});
}
inline Vec3 tason_normaali(const Kappale& taso) {
    return kierra(taso.kierto, {0, 1, 0});
}
inline void taso_pallo(const Kappale& taso, const Kappale& b, Monisto& m) {
    Vec3 n = tason_normaali(taso);
    double korkeus = piste(b.sijainti - taso.sijainti, n);
    if (korkeus >= b.muoto.sade + MARGINAALI) return;
    m.normaali = n;
    m.pisteet.push_back({b.sijainti - b.muoto.sade * n,
                         b.muoto.sade - korkeus});
}
// @loppu pallot

// @alku laatikko-apu
// Laatikon akselit maailmassa ja kahdeksan kärkeä.
struct Akselit {
    Vec3 u[3];
};
inline Akselit akselit(const Kappale& k) {
    Mat3 r = kiertomatriisi(k.kierto);
    return {{sarake(r, 0), sarake(r, 1), sarake(r, 2)}};
}
inline double komponentti(Vec3 v, int i) {
    return i == 0 ? v.x : i == 1 ? v.y : v.z;
}
inline std::array<Vec3, 8> karjet(const Kappale& k) {
    Akselit ak = akselit(k);
    std::array<Vec3, 8> p;
    for (int i = 0; i < 8; ++i)
        p[i] = k.sijainti +
               ((i & 1 ? 1 : -1) * k.muoto.puolet.x) * ak.u[0] +
               ((i & 2 ? 1 : -1) * k.muoto.puolet.y) * ak.u[1] +
               ((i & 4 ? 1 : -1) * k.muoto.puolet.z) * ak.u[2];
    return p;
}
// @loppu laatikko-apu

// @alku taso-laatikko
// Jokainen tason alle (tai marginaalin sisään) jäänyt kärki on
// kosketuspiste. Lappeellaan lepäävä laatikko saa neljä pistettä, mikä
// pitää sen vakaana.
inline void taso_laatikko(const Kappale& taso, const Kappale& b,
                          Monisto& m) {
    Vec3 n = tason_normaali(taso);
    for (Vec3 p : karjet(b)) {
        double korkeus = piste(p - taso.sijainti, n);
        if (korkeus < MARGINAALI) m.pisteet.push_back({p, -korkeus});
    }
    m.normaali = n;
}
// @loppu taso-laatikko

// @alku pallo-laatikko
// Pallon keskipiste viedään laatikon koordinaatistoon, jossa lähin
// piste saadaan rajaamalla koordinaatit puolimittoihin.
inline void pallo_laatikko(const Kappale& a, const Kappale& b, Monisto& m) {
    Akselit ak = akselit(b);
    Vec3 d = a.sijainti - b.sijainti, e = b.muoto.puolet;
    Vec3 paik{piste(d, ak.u[0]), piste(d, ak.u[1]), piste(d, ak.u[2])};
    Vec3 lahin{std::clamp(paik.x, -e.x, e.x), std::clamp(paik.y, -e.y, e.y),
               std::clamp(paik.z, -e.z, e.z)};
    Vec3 ero = paik - lahin;
    double etaisyys = pituus(ero);
    if (etaisyys >= a.muoto.sade + MARGINAALI) return;
    Vec3 n_paik;  // laatikosta palloon, laatikon koordinaateissa
    double syvyys;
    if (etaisyys > 1e-9) {
        n_paik = (1 / etaisyys) * ero;
        syvyys = a.muoto.sade - etaisyys;
    } else {
        // Keskipiste on laatikon sisällä: ulos lähimmän sivun kautta.
        int paras = 0;
        double pienin = 1e30;
        for (int i = 0; i < 3; ++i) {
            double vara = komponentti(e, i) - std::abs(komponentti(paik, i));
            if (vara < pienin) {
                pienin = vara;
                paras = i;
            }
        }
        double merkki = komponentti(paik, paras) < 0 ? -1 : 1;
        n_paik = {paras == 0 ? merkki : 0, paras == 1 ? merkki : 0,
                  paras == 2 ? merkki : 0};
        syvyys = a.muoto.sade + pienin;
    }
    Vec3 n = n_paik.x * ak.u[0] + n_paik.y * ak.u[1] + n_paik.z * ak.u[2];
    m.normaali = -n;  // pallosta (a) laatikkoon (b)
    m.pisteet.push_back({a.sijainti - a.muoto.sade * n, syvyys});
}
// @loppu pallo-laatikko

// @alku sat
// Erottavan akselin lause kahdelle laatikolle: 3 + 3 sivunormaalia ja
// 9 särmäparien ristituloa. Pienin tunkeuma kertoo normaalin.
struct Akselitulos {
    bool erillaan = true;
    double syvyys = 1e30;
    Vec3 normaali;       // a:sta b:hen
    int laji = 0;        // 0: a:n sivu, 1: b:n sivu, 2: särmäpari
    int ia = 0, ib = 0;  // akselien indeksit
};
inline double puoliprojektio(const Akselit& ak, Vec3 e, Vec3 suunta) {
    return e.x * std::abs(piste(ak.u[0], suunta)) +
           e.y * std::abs(piste(ak.u[1], suunta)) +
           e.z * std::abs(piste(ak.u[2], suunta));
}
inline Akselitulos erottava_akseli(const Kappale& a, const Kappale& b) {
    Akselit aa = akselit(a), ab = akselit(b);
    Vec3 d = b.sijainti - a.sijainti;
    Akselitulos paras;
    auto kokeile = [&](Vec3 suunta, int laji, int ia, int ib) {
        double p = pituus(suunta);
        if (p < 1e-6) return true;  // samansuuntaiset särmät: ohita
        suunta = (1 / p) * suunta;
        double syvyys = puoliprojektio(aa, a.muoto.puolet, suunta) +
                        puoliprojektio(ab, b.muoto.puolet, suunta) -
                        std::abs(piste(d, suunta));
        if (syvyys < -MARGINAALI) return false;  // erottava akseli
        // Särmäakseli hyväksytään vain, jos se on selvästi sivuja
        // parempi: sivukosketus antaa vakaamman moniston.
        double vertailu = laji == 2 ? syvyys * 1.05 + 1e-4 : syvyys;
        if (vertailu < paras.syvyys) {
            paras.syvyys = syvyys;
            paras.normaali = piste(d, suunta) < 0 ? -suunta : suunta;
            paras.laji = laji;
            paras.ia = ia;
            paras.ib = ib;
        }
        return true;
    };
    for (int i = 0; i < 3; ++i)
        if (!kokeile(aa.u[i], 0, i, 0)) return {};
    for (int j = 0; j < 3; ++j)
        if (!kokeile(ab.u[j], 1, 0, j)) return {};
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            if (!kokeile(risti(aa.u[i], ab.u[j]), 2, i, j)) return {};
    paras.erillaan = false;
    return paras;
}
// @loppu sat

// @alku leikkaus
// Monikulmio leikataan puoliavaruuteen piste(n, p) <= raja
// (Sutherland-Hodgman, tuttu taidosta Renderöinnin perusteet).
inline std::vector<Vec3> leikkaa(const std::vector<Vec3>& monikulmio,
                                 Vec3 n, double raja) {
    std::vector<Vec3> tulos;
    for (std::size_t i = 0; i < monikulmio.size(); ++i) {
        Vec3 p = monikulmio[i], q = monikulmio[(i + 1) % monikulmio.size()];
        double dp = piste(n, p) - raja, dq = piste(n, q) - raja;
        if (dp <= 0) tulos.push_back(p);
        if ((dp < 0 && dq > 0) || (dp > 0 && dq < 0))
            tulos.push_back(p + (dp / (dp - dq)) * (q - p));
    }
    return tulos;
}

// Sivukosketus: viitelaatikon sivu on se, jonka normaali on kosketuksen
// normaali. Toisen laatikon vastakkainen sivu (tulosivu) leikataan
// viitesivun reunoihin, ja viitesivun alle jääneet pisteet ovat
// kosketuspisteitä. n osoittaa viitelaatikosta ulos.
inline void sivukosketus(const Kappale& viite, int akseli, Vec3 n,
                         const Kappale& tulo, Monisto& m) {
    Akselit av = akselit(viite), at = akselit(tulo);
    // Tulosivu: se tulolaatikon sivu, jonka normaali on eniten n:ää
    // vastaan.
    int j = 0;
    for (int k = 1; k < 3; ++k)
        if (std::abs(piste(at.u[k], n)) > std::abs(piste(at.u[j], n))) j = k;
    double merkki = piste(at.u[j], n) > 0 ? -1 : 1;
    int j1 = (j + 1) % 3, j2 = (j + 2) % 3;
    Vec3 keskus = tulo.sijainti +
                  (merkki * komponentti(tulo.muoto.puolet, j)) * at.u[j];
    Vec3 s1 = komponentti(tulo.muoto.puolet, j1) * at.u[j1];
    Vec3 s2 = komponentti(tulo.muoto.puolet, j2) * at.u[j2];
    std::vector<Vec3> sivu = {keskus - s1 - s2, keskus + s1 - s2,
                              keskus + s1 + s2, keskus - s1 + s2};
    // Leikkaus viitesivun neljään reunatasoon.
    for (int k = 1; k <= 2; ++k) {
        int i = (akseli + k) % 3;
        Vec3 u = av.u[i];
        double e = komponentti(viite.muoto.puolet, i);
        double keski = piste(u, viite.sijainti);
        sivu = leikkaa(sivu, u, keski + e);
        sivu = leikkaa(sivu, -u, -keski + e);
    }
    double pinta = piste(n, viite.sijainti) +
                   komponentti(viite.muoto.puolet, akseli);
    for (Vec3 p : sivu) {
        double syvyys = pinta - piste(n, p);
        if (syvyys >= -MARGINAALI) m.pisteet.push_back({p, syvyys});
    }
}
// @loppu leikkaus

// @alku sarmat
// Särmäkosketus: yksi piste kahden särmän lähimpien pisteiden välistä.
inline void sarmakosketus(const Kappale& a, const Kappale& b,
                          const Akselitulos& t, Monisto& m) {
    Akselit aa = akselit(a), ab = akselit(b);
    // Särmän keskipiste: laatikon kauimmainen kohta normaalin suunnassa
    // kahdella muulla akselilla.
    Vec3 pa = a.sijainti, pb = b.sijainti;
    for (int k = 0; k < 3; ++k) {
        if (k != t.ia)
            pa = pa + ((piste(aa.u[k], t.normaali) > 0 ? 1 : -1) *
                       komponentti(a.muoto.puolet, k)) * aa.u[k];
        if (k != t.ib)
            pb = pb + ((piste(ab.u[k], t.normaali) > 0 ? -1 : 1) *
                       komponentti(b.muoto.puolet, k)) * ab.u[k];
    }
    // Kahden suoran lähimmät pisteet (vrt. janojen lähimmät pisteet
    // taidossa 3D-peliohjelmointi).
    Vec3 da = aa.u[t.ia], db = ab.u[t.ib], r = pa - pb;
    double bb = piste(da, db), c = piste(da, r), f = piste(db, r);
    double nimittaja = 1 - bb * bb;
    double s = nimittaja > 1e-9 ? (bb * f - c) / nimittaja : 0;
    double u = f + bb * s;
    m.pisteet.push_back({0.5 * ((pa + s * da) + (pb + u * db)), t.syvyys});
}
// @loppu sarmat

// @alku laatikot
inline void laatikko_laatikko(const Kappale& a, const Kappale& b,
                              Monisto& m) {
    Akselitulos t = erottava_akseli(a, b);
    if (t.erillaan) return;
    m.normaali = t.normaali;
    if (t.laji == 0)
        sivukosketus(a, t.ia, t.normaali, b, m);
    else if (t.laji == 1)
        sivukosketus(b, t.ib, -t.normaali, a, m);
    else
        sarmakosketus(a, b, t, m);
}
// @loppu laatikot

// @alku kosketa
// Valitsee testin muotojen lajin mukaan. Parit käsitellään aina
// järjestyksessä taso < pallo < laatikko, ja normaali käännetään, jos
// kappaleet piti vaihtaa keskenään.
inline Monisto kosketa(const std::vector<Kappale>& kappaleet, int ia,
                       int ib) {
    using L = Muoto::Laji;
    bool vaihda = kappaleet[ia].muoto.laji > kappaleet[ib].muoto.laji;
    const Kappale& a = kappaleet[vaihda ? ib : ia];
    const Kappale& b = kappaleet[vaihda ? ia : ib];
    Monisto m;
    m.a = ia;
    m.b = ib;
    if (a.muoto.laji == L::taso && b.muoto.laji == L::pallo)
        taso_pallo(a, b, m);
    else if (a.muoto.laji == L::taso && b.muoto.laji == L::laatikko)
        taso_laatikko(a, b, m);
    else if (a.muoto.laji == L::pallo && b.muoto.laji == L::pallo)
        pallo_pallo(a, b, m);
    else if (a.muoto.laji == L::pallo && b.muoto.laji == L::laatikko)
        pallo_laatikko(a, b, m);
    else if (a.muoto.laji == L::laatikko && b.muoto.laji == L::laatikko)
        laatikko_laatikko(a, b, m);
    if (vaihda) m.normaali = -m.normaali;
    return m;
}
// @loppu kosketa
