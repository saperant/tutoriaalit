// Lukujen tulostus testattavassa muodossa: kiinteä tarkkuus, ja hyvin
// pieni negatiivinen luku tulostuu nollana eikä muodossa -0.00.
#pragma once
#include "vektori.hpp"

#include <format>
#include <string>

inline std::string luku(double x, int desimaalit = 2) {
    double raja = 0.5;
    for (int i = 0; i < desimaalit; ++i) raja /= 10;
    if (std::abs(x) < raja) x = 0;
    return std::format("{:.{}f}", x, desimaalit);
}
inline std::string teksti(Vec3 v, int desimaalit = 2) {
    return std::format("({}, {}, {})", luku(v.x, desimaalit),
                       luku(v.y, desimaalit), luku(v.z, desimaalit));
}
