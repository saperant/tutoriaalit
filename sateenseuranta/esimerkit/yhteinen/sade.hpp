// Säde ja leikkaukset: pallo, taso, kolmio ja laatikko.
#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include <utility>

#include "vektori.hpp"

// @alku sade
// Säde o + t d, kun t > 0. Suunta d on yksikkövektori, joten t on
// etäisyys lähtöpisteestä.
struct Sade {
    Vec3 o, d;
};
inline Vec3 kohta(const Sade& s, double t) { return s.o + t * s.d; }
constexpr double AARETON = std::numeric_limits<double>::infinity();
// @loppu sade

// @alku pallo
struct Pallo {
    Vec3 keski;
    double r;
};
// Lähin leikkaus väliltä (tmin, tmax), muuten AARETON. Toisen asteen
// yhtälö t^2 - 2bt + c = 0 ratkaistaan vakaasti: diskriminantti
// kohtisuorasta etäisyydestä ja pienempi juuri muodossa c / q
// (Haines ym., Ray Tracing Gems 2019, luku 7).
inline double leikkaa_pallo(const Pallo& p, const Sade& s, double tmin,
                            double tmax) {
    Vec3 f = s.o - p.keski;
    double b = -piste(f, s.d);     // säteen lähin kohta keskipistettä
    Vec3 l = f + b * s.d;          // keskipisteestä säteen lähimpään
    double diskr = p.r * p.r - piste(l, l);
    if (diskr < 0) return AARETON;           // ohi
    double c = piste(f, f) - p.r * p.r;
    double q = b + std::copysign(std::sqrt(diskr), b);
    if (q == 0) return AARETON;              // sivuaa lähtöpisteessä
    double t0 = c / q, t1 = q;
    if (t0 > t1) std::swap(t0, t1);
    if (t0 > tmin && t0 < tmax) return t0;   // ulkoa sisään
    if (t1 > tmin && t1 < tmax) return t1;   // sisältä ulos
    return AARETON;
}
// @loppu pallo

// @alku taso
// Taso: pisteet p, joille piste(n, p) = e; n on yksikkönormaali.
struct Taso {
    Vec3 n;
    double e;
};
inline double leikkaa_taso(const Taso& T, const Sade& s, double tmin,
                           double tmax) {
    double nd = piste(T.n, s.d);
    if (std::fabs(nd) < 1e-12) return AARETON;  // tason suuntainen
    double t = (T.e - piste(T.n, s.o)) / nd;
    return t > tmin && t < tmax ? t : AARETON;
}
// @loppu taso

// @alku kolmio
struct Kolmio {
    Vec3 a, b, c;
};
// Etäisyys ja barysentriset painot u (kärki b) ja v (kärki c).
struct KolmioOsuma {
    double t = AARETON, u = 0, v = 0;
};
// Möller–Trumbore (1997): ratkaisee yhtälön o + t d = a + u e1 + v e2
// Cramerin säännöllä ilman tason yhtälöä.
inline KolmioOsuma leikkaa_kolmio(const Kolmio& k, const Sade& s,
                                  double tmin, double tmax) {
    Vec3 e1 = k.b - k.a, e2 = k.c - k.a;
    Vec3 p = risti(s.d, e2);
    double det = piste(e1, p);
    if (std::fabs(det) < 1e-12) return {};   // säde tason suuntainen
    double kaanteis = 1 / det;
    Vec3 w = s.o - k.a;
    double u = piste(w, p) * kaanteis;
    if (u < 0 || u > 1) return {};
    Vec3 q = risti(w, e1);
    double v = piste(s.d, q) * kaanteis;
    if (v < 0 || u + v > 1) return {};
    double t = piste(e2, q) * kaanteis;
    if (t <= tmin || t >= tmax) return {};
    return {t, u, v};
}
// Kolmion geometrinen normaali kärkien kiertosuunnan mukaan.
inline Vec3 normaali(const Kolmio& k) {
    return normalisoi(risti(k.b - k.a, k.c - k.a));
}
// @loppu kolmio

// @alku laatikko
// Akselien suuntainen laatikko (AABB). Tyhjä laatikko on käänteinen.
struct Laatikko {
    Vec3 min{AARETON, AARETON, AARETON};
    Vec3 max{-AARETON, -AARETON, -AARETON};
};
// @loppu laatikko

// @alku yhdiste
// Yhdiste: tyhjä laatikko (min > max) ei muuta tulosta.
inline void laajenna(Laatikko& b, const Laatikko& c) {
    b.min = {std::min(b.min.x, c.min.x), std::min(b.min.y, c.min.y),
             std::min(b.min.z, c.min.z)};
    b.max = {std::max(b.max.x, c.max.x), std::max(b.max.y, c.max.y),
             std::max(b.max.z, c.max.z)};
}
inline void laajenna(Laatikko& b, Vec3 p) { laajenna(b, Laatikko{p, p}); }
inline double pinta_ala(const Laatikko& b) {
    Vec3 d = b.max - b.min;
    return 2 * (d.x * d.y + d.y * d.z + d.z * d.x);
}
// @loppu yhdiste

// @alku laatta
// Suunnan käänteisluvut lasketaan kerran säteelle. Nollasta tulee
// etumerkillinen ääretön, jolloin kyseinen akseli ei rajaa väliä.
inline Vec3 kaanteinen(Vec3 d) {
    auto k = [](double x) { return x == 0 ? std::copysign(AARETON, x)
                                          : 1 / x; };
    return {k(d.x), k(d.y), k(d.z)};
}
// Laattamenetelmä (slab test): kunkin akselin kahden tason välissä
// säde on välillä [t0, t1]; laatikossa se on välien leikkauksessa.
// Palauttaa välin alun tai AARETON, jos väli on tyhjä.
inline double leikkaa_laatikko(const Laatikko& b, const Sade& s,
                               Vec3 kaanteis, double tmin, double tmax) {
    for (int i = 0; i < 3; ++i) {
        double t0 = (akseli(b.min, i) - akseli(s.o, i)) *
                    akseli(kaanteis, i);
        double t1 = (akseli(b.max, i) - akseli(s.o, i)) *
                    akseli(kaanteis, i);
        if (t0 > t1) std::swap(t0, t1);
        // Vertailu päin tätä: NaN (0 * ääretön) jättää välin ennalleen.
        tmin = t0 > tmin ? t0 : tmin;
        tmax = t1 < tmax ? t1 : tmax;
        if (tmax < tmin) return AARETON;
    }
    return tmin;
}
// @loppu laatta
