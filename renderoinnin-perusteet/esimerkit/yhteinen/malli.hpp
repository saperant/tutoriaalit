// Kolmioverkot: kuutio, pallo ja taso.
#pragma once
#include <array>
#include <vector>

#include "vektori.hpp"

// @alku malli
struct Verteksi {
    Vec3 paikka;
    Vec3 normaali;
    Vec2 uv;
};
// Kolmiot ovat vastapäivään ulkoa katsottuna (etupinta).
struct Malli {
    std::vector<Verteksi> verteksit;
    std::vector<std::array<int, 3>> kolmiot;

    void nelikulmio(Verteksi a, Verteksi b, Verteksi c, Verteksi d) {
        int i = static_cast<int>(verteksit.size());
        verteksit.insert(verteksit.end(), {a, b, c, d});
        kolmiot.push_back({i, i + 1, i + 2});
        kolmiot.push_back({i, i + 2, i + 3});
    }
};
// @loppu malli

// @alku kuutio
// Kuutio [-1, 1]^3. Jokaisella sivulla omat kärjet, jotta normaali
// ja tekstuurikoordinaatit voivat olla sivukohtaisia.
inline Malli kuutio() {
    struct Sivu {
        Vec3 n, u, v;  // normaali ja sivun akselit, u x v = n
    };
    const Sivu sivut[6] = {
        {{1, 0, 0}, {0, 0, -1}, {0, 1, 0}},
        {{-1, 0, 0}, {0, 0, 1}, {0, 1, 0}},
        {{0, 1, 0}, {1, 0, 0}, {0, 0, -1}},
        {{0, -1, 0}, {1, 0, 0}, {0, 0, 1}},
        {{0, 0, 1}, {1, 0, 0}, {0, 1, 0}},
        {{0, 0, -1}, {-1, 0, 0}, {0, 1, 0}},
    };
    Malli m;
    for (const Sivu& s : sivut) {
        auto kulma = [&s](double a, double b) {
            return Verteksi{s.n + a * s.u + b * s.v, s.n,
                            {(a + 1) / 2, (1 - b) / 2}};
        };
        m.nelikulmio(kulma(-1, -1), kulma(1, -1), kulma(1, 1),
                     kulma(-1, 1));
    }
    return m;
}
// @loppu kuutio

// @alku pallo
// Yksikköpallo oktaedrista: jokainen kolmio jaetaan neljään ja uudet
// kärjet työnnetään pallon pinnalle. Normaali on sama kuin paikka.
inline void jaa(Malli& m, Vec3 a, Vec3 b, Vec3 c, int tasot) {
    if (tasot == 0) {
        int i = static_cast<int>(m.verteksit.size());
        for (Vec3 p : {a, b, c}) m.verteksit.push_back({p, p, {}});
        m.kolmiot.push_back({i, i + 1, i + 2});
        return;
    }
    Vec3 ab = normalisoi(a + b), bc = normalisoi(b + c);
    Vec3 ca = normalisoi(c + a);
    jaa(m, a, ab, ca, tasot - 1);
    jaa(m, ab, b, bc, tasot - 1);
    jaa(m, ca, bc, c, tasot - 1);
    jaa(m, ab, bc, ca, tasot - 1);
}
inline Malli pallo(int tasot) {
    Malli m;
    for (int sx : {1, -1})
        for (int sy : {1, -1})
            for (int sz : {1, -1}) {
                Vec3 x{1.0 * sx, 0, 0}, y{0, 1.0 * sy, 0};
                Vec3 z{0, 0, 1.0 * sz};
                if (sx * sy * sz > 0) jaa(m, x, y, z, tasot);
                else jaa(m, x, z, y, tasot);
            }
    return m;
}
// @loppu pallo

// @alku taso
// Vaakataso y = 0, sivu 2 * puoli; tekstuuri toistuu toisto kertaa.
inline Malli taso(double puoli, double toisto) {
    Malli m;
    auto kulma = [=](double a, double b) {
        return Verteksi{{a * puoli, 0, -b * puoli}, {0, 1, 0},
                        {(a + 1) / 2 * toisto, (1 - b) / 2 * toisto}};
    };
    m.nelikulmio(kulma(-1, -1), kulma(1, -1), kulma(1, 1), kulma(-1, 1));
    return m;
}
// @loppu taso
