// Kolmioverkot: yksinkertaiset muodot koodista ja verkon piirto.
#pragma once
#include "piirto.hpp"
#include "tormays.hpp"

#include <array>
#include <vector>

// @alku verkko
struct Verkko {
    std::vector<Vec3> pisteet;
    std::vector<std::array<int, 3>> kolmiot;  // indeksit, vastapäivään
};
// Verkon kolmiot maailmakoordinaatteihin, esimerkiksi törmäystä varten.
inline std::vector<Kolmio> kolmioiksi(const Verkko& v, const Mat4& malli) {
    std::vector<Kolmio> tulos;
    for (auto [a, b, c] : v.kolmiot)
        tulos.push_back({muunna_piste(malli, v.pisteet[a]),
                         muunna_piste(malli, v.pisteet[b]),
                         muunna_piste(malli, v.pisteet[c])});
    return tulos;
}
// @loppu verkko

inline void lisaa_nelio(Verkko& v, Vec3 a, Vec3 b, Vec3 c, Vec3 d) {
    int i = static_cast<int>(v.pisteet.size());
    v.pisteet.insert(v.pisteet.end(), {a, b, c, d});
    v.kolmiot.push_back({i, i + 1, i + 2});
    v.kolmiot.push_back({i, i + 2, i + 3});
}

inline Verkko laatikkoverkko(Vec3 lo, Vec3 hi) {
    Verkko v;
    Vec3 p[8];
    for (int i = 0; i < 8; ++i)
        p[i] = {i & 1 ? hi.x : lo.x, i & 2 ? hi.y : lo.y,
                i & 4 ? hi.z : lo.z};
    lisaa_nelio(v, p[4], p[5], p[7], p[6]);  // +z
    lisaa_nelio(v, p[1], p[0], p[2], p[3]);  // -z
    lisaa_nelio(v, p[5], p[1], p[3], p[7]);  // +x
    lisaa_nelio(v, p[0], p[4], p[6], p[2]);  // -x
    lisaa_nelio(v, p[6], p[7], p[3], p[2]);  // +y
    lisaa_nelio(v, p[0], p[1], p[5], p[4]);  // -y
    return v;
}

// Pallo leveys- ja pituuspiirien ruudukkona.
inline Verkko palloverkko(double sade, int lohkot = 12) {
    Verkko v;
    auto p = [sade, lohkot](int i, int j) {
        double lev = PII * i / lohkot, pit = 2 * PII * j / lohkot;
        return Vec3{sade * std::sin(lev) * std::cos(pit),
                    sade * std::cos(lev),
                    -sade * std::sin(lev) * std::sin(pit)};
    };
    for (int i = 0; i < lohkot; ++i)
        for (int j = 0; j < lohkot; ++j)
            lisaa_nelio(v, p(i, j), p(i + 1, j), p(i + 1, j + 1),
                        p(i, j + 1));
    return v;
}

// Pystysuora kapseli: jana (0, r, 0)-(0, korkeus - r, 0) ja säde r.
inline Verkko kapseliverkko(double sade, double korkeus, int lohkot = 12) {
    Verkko v = palloverkko(sade, lohkot);
    for (Vec3& p : v.pisteet)  // yläpuolisko ylös, alapuolisko alas
        p.y += p.y >= 0 ? korkeus - sade : sade;
    return v;
}

inline void piirra(Piirtaja& piirtaja, const Verkko& v, const Mat4& malli,
                   Vari vari) {
    for (const Kolmio& k : kolmioiksi(v, malli))
        piirtaja.kolmio(k.a, k.b, k.c, vari);
}

// Laatikon reunat viivoina (törmäyslaatikoiden vianetsintäkuvat).
inline void piirra_reunat(Piirtaja& piirtaja, const Laatikko& l, Vari vari,
                          bool paalle = false) {
    Vec3 p[8];
    for (int i = 0; i < 8; ++i)
        p[i] = {i & 1 ? l.max.x : l.min.x, i & 2 ? l.max.y : l.min.y,
                i & 4 ? l.max.z : l.min.z};
    for (int i = 0; i < 8; ++i)
        for (int bitti : {1, 2, 4})
            if (!(i & bitti))
                piirtaja.viiva(p[i], p[i | bitti], vari, paalle);
}

// Ruudutettu lattia tasolla y = 0.
inline void piirra_lattia(Piirtaja& piirtaja, int ruutuja, double koko,
                          Vari a, Vari b) {
    for (int i = -ruutuja; i < ruutuja; ++i)
        for (int j = -ruutuja; j < ruutuja; ++j) {
            Vec3 p{i * koko, 0, j * koko};
            Vari v = (i + j) & 1 ? a : b;
            piirtaja.kolmio(p, p + Vec3{0, 0, koko}, p + Vec3{koko, 0, koko},
                            v);
            piirtaja.kolmio(p, p + Vec3{koko, 0, koko}, p + Vec3{koko, 0, 0},
                            v);
        }
}
