// Suuntien näytteistys pallonpuoliskolla ja kartiossa.
#pragma once
#include <algorithm>
#include <cmath>

#include "vektori.hpp"

constexpr double PII = 3.14159265358979323846;

// @alku naytteet
// Kaikki suunnat ovat paikallisessa kannassa, jossa normaali on z.
// u1 ja u2 ovat tasajakautuneita välillä [0, 1).

// Tasainen suunta pallonpuoliskolla: pdf = 1 / (2 pi).
inline Vec3 tasainen_puolipallo(double u1, double u2) {
    double z = u1, r = std::sqrt(1 - z * z), phi = 2 * PII * u2;
    return {r * std::cos(phi), r * std::sin(phi), z};
}
// Kosinipainotettu suunta: pdf = cos(theta) / pi. Kiekolta tasaisesti
// valittu piste nostetaan pallonpuoliskolle (Malleyn menetelmä).
inline Vec3 kosinipainotettu(double u1, double u2) {
    double r = std::sqrt(u1), phi = 2 * PII * u2;
    return {r * std::cos(phi), r * std::sin(phi), std::sqrt(1 - u1)};
}
// Tasainen suunta kartiossa, jonka puolikulman kosini on cmax:
// pdf = 1 / (2 pi (1 - cmax)).
inline Vec3 kartio(double u1, double u2, double cmax) {
    double z = 1 - u1 * (1 - cmax);
    double r = std::sqrt(std::max(0.0, 1 - z * z)), phi = 2 * PII * u2;
    return {r * std::cos(phi), r * std::sin(phi), z};
}
// @loppu naytteet
