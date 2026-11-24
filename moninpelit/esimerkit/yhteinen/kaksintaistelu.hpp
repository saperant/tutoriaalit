// Pieni deterministinen kahden pelaajan peli lukitusaskel- ja
// rollback-esimerkkeihin. Kaikki laskenta kokonaisluvuilla.
#pragma once
#include <array>
#include <cstdint>

// @alku peli
using Syote = std::uint8_t;  // bitit: 1 vasen, 2 oikea, 4 hyppy

struct Tila {
    std::array<std::int32_t, 2> x{-300, 300}, y{0, 0}, vy{0, 0};
    std::array<std::int32_t, 2> pisteet{0, 0};
    std::uint32_t ruutu = 0;
};

// Yksi ruutu eteenpäin molempien pelaajien syötteillä.
inline void askel(Tila& t, std::array<Syote, 2> s) {
    for (int p = 0; p < 2; ++p) {
        t.x[p] += ((s[p] & 2) ? 7 : 0) - ((s[p] & 1) ? 7 : 0);
        if ((s[p] & 4) && t.y[p] == 0) {
            t.vy[p] = 40;
        }
        t.y[p] += t.vy[p];
        t.vy[p] -= 3;
        if (t.y[p] <= 0) {
            t.y[p] = 0;
            t.vy[p] = 0;
        }
    }
    // Hyppääjä saa pisteen, kun laskeutuu toisen päälle.
    for (int p = 0; p < 2; ++p) {
        const int q = 1 - p;
        const std::int32_t dx = t.x[p] - t.x[q];
        if (t.vy[p] < 0 && t.y[p] > 0 && t.y[p] < 30 && dx > -40 &&
            dx < 40) {
            ++t.pisteet[p];
            t.x[q] = -t.x[q];
        }
    }
    ++t.ruutu;
}

// FNV-1a koko tilan yli: sama luku = sama tila.
inline std::uint32_t tarkistussumma(const Tila& t) {
    std::uint32_t h = 2166136261u;
    auto lisaa = [&](std::int32_t v) {
        for (int i = 0; i < 4; ++i) {
            h = (h ^ ((static_cast<std::uint32_t>(v) >> (8 * i)) & 0xffu)) *
                16777619u;
        }
    };
    for (int p = 0; p < 2; ++p) {
        lisaa(t.x[p]);
        lisaa(t.y[p]);
        lisaa(t.vy[p]);
        lisaa(t.pisteet[p]);
    }
    lisaa(static_cast<std::int32_t>(t.ruutu));
    return h;
}
// @loppu peli
