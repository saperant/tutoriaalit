// Materiaalit: Lambert, peili, lasi ja mikrofasettimalli (GGX).
#pragma once
#include <algorithm>
#include <cmath>
#include <optional>

#include "kuva.hpp"
#include "naytteet.hpp"
#include "satunnainen.hpp"
#include "vektori.hpp"

// @alku materiaali
struct Materiaali {
    enum Laji { diffuusi, peili, lasi, karhea };
    Laji laji = diffuusi;
    Vari vari{0.8, 0.8, 0.8};  // heijastuskyky tai metallin F0
    Vari sateily{};            // pinnan lähettämä radianssi
    double karheus = 0.5;      // GGX: alfa = karheus^2
    double metalli = 0;        // 0 = eriste, 1 = metalli
    double taitekerroin = 1.5;
};
// @loppu materiaali

// @alku fresnel
// Fresnelin yhtälöt polaroimattomalle valolle eristeen rajapinnassa.
// eta = n1 / n2 (tulopuoli / läpäisypuoli), cos_i > 0.
inline double fresnel(double cos_i, double eta) {
    double sin2_t = eta * eta * (1 - cos_i * cos_i);
    if (sin2_t >= 1) return 1;                 // kokonaisheijastus
    double cos_t = std::sqrt(1 - sin2_t);
    double rs = (eta * cos_i - cos_t) / (eta * cos_i + cos_t);
    double rp = (cos_i - eta * cos_t) / (cos_i + eta * cos_t);
    return (rs * rs + rp * rp) / 2;
}
// Schlickin approksimaatio: F0 + (1 - F0)(1 - cos)^5.
inline double schlick(double f0, double c) {
    double m = 1 - c, m2 = m * m;
    return f0 + (1 - f0) * m2 * m2 * m;
}
// Taittunut suunta Snellin laista tai tyhjä kokonaisheijastuksessa.
// d tulee pintaan, n osoittaa tulopuolelle.
inline std::optional<Vec3> taita(Vec3 d, Vec3 n, double eta) {
    double cos_i = -piste(d, n);
    double sin2_t = eta * eta * (1 - cos_i * cos_i);
    if (sin2_t >= 1) return std::nullopt;
    return eta * d + (eta * cos_i - std::sqrt(1 - sin2_t)) * n;
}
// @loppu fresnel

// @alku ggx
// GGX- eli Trowbridge–Reitz-jakauma: mikrofasettien normaalien h
// tiheys. alfa = karheus^2 (Burley 2012).
inline double ggx_d(double nh, double alfa) {
    double a2 = alfa * alfa, k = nh * nh * (a2 - 1) + 1;
    return a2 / (PII * k * k);
}
// Smithin varjostus- ja peittotermi yhdelle suunnalle.
inline double smith_g1(double nv, double alfa) {
    double a2 = alfa * alfa;
    return 2 * nv / (nv + std::sqrt(a2 + (1 - a2) * nv * nv));
}
// Mikrofasettinormaali jakaumasta D(h) cos(theta_h).
inline Vec3 ggx_normaali(double u1, double u2, double alfa) {
    double c2 = (1 - u1) / (1 + (alfa * alfa - 1) * u1);
    double c = std::sqrt(c2), s = std::sqrt(1 - c2), phi = 2 * PII * u2;
    return {s * std::cos(phi), s * std::sin(phi), c};
}
// @loppu ggx

// @alku brdf
// BRDF f(v, l) paikallisessa kannassa (normaali z). v osoittaa
// katsojaan ja l valoon; kumpikin on yksikkövektori.
inline Vari brdf(const Materiaali& m, Vec3 v, Vec3 l) {
    if (v.z <= 0 || l.z <= 0) return {};
    if (m.laji == Materiaali::diffuusi) return (1 / PII) * m.vari;
    double alfa = m.karheus * m.karheus;
    Vec3 h = normalisoi(v + l);
    double vh = piste(v, h);
    double dg = ggx_d(h.z, alfa) * smith_g1(v.z, alfa) *
                smith_g1(l.z, alfa) / (4 * v.z * l.z);
    // Metallilla F0 on pinnan väri, eristeellä 4 % ja väri on alla.
    // Alla oleva diffuusikerros saa valon, joka ei heijastunut
    // pinnasta sisään eikä ulos tullessa (Shirley ym. 1997).
    auto kanava = [&](double vari) {
        double f0 = 0.04 + (vari - 0.04) * m.metalli;
        double sisaan = 1 - schlick(f0, l.z), ulos = 1 - schlick(f0, v.z);
        return dg * schlick(f0, vh) +
               (1 - m.metalli) * sisaan * ulos * vari / PII;
    };
    return {kanava(m.vari.r), kanava(m.vari.g), kanava(m.vari.b)};
}
// @loppu brdf

// @alku poiminta
// Suunnan l todennäköisyystiheys, kun se poimitaan kuten poimi().
inline double pdf(const Materiaali& m, Vec3 v, Vec3 l) {
    if (l.z <= 0) return 0;
    if (m.laji == Materiaali::diffuusi) return l.z / PII;
    double alfa = m.karheus * m.karheus, ps = (1 + m.metalli) / 2;
    Vec3 h = normalisoi(v + l);
    double peili = ggx_d(h.z, alfa) * h.z / (4 * piste(v, h));
    return ps * peili + (1 - ps) * l.z / PII;
}
// Poimii suunnan l ja palauttaa painon f cos / pdf (musta, jos
// suunta jäi pinnan alle). Karhealla pinnalla kaksi lohkoa:
// GGX-heijastus todennäköisyydellä ps ja kosinilohko muuten.
inline Vari poimi(const Materiaali& m, Vec3 v, Pcg32& g, Vec3& l) {
    double u1 = g.tasainen(), u2 = g.tasainen();
    if (m.laji == Materiaali::diffuusi) {
        l = kosinipainotettu(u1, u2);
        return m.vari;                       // (vari/pi) cos / (cos/pi)
    }
    double alfa = m.karheus * m.karheus, ps = (1 + m.metalli) / 2;
    if (g.tasainen() < ps)
        l = heijasta(-v, ggx_normaali(u1, u2, alfa));
    else
        l = kosinipainotettu(u1, u2);
    if (l.z <= 0) return {};
    return (l.z / pdf(m, v, l)) * brdf(m, v, l);
}
// @loppu poiminta
