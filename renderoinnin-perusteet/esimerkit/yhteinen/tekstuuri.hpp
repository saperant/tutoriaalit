// Tekstuurit: näytteenotto, suodatus ja mipmapit.
#pragma once
#include <algorithm>
#include <cmath>
#include <vector>

#include "kuva.hpp"
#include "vektori.hpp"

// @alku tekstuuri
// Tekseleinä lineaarisia värejä, jotta suodatus laskee valon määrillä.
// Koordinaatit toistuvat: u = 1.25 on sama kuin u = 0.25.
struct Tekstuuri {
    int l = 0, k = 0;
    std::vector<Vari> t;

    Vari tekseli(int x, int y) const {
        x = ((x % l) + l) % l;
        y = ((y % k) + k) % k;
        return t[static_cast<std::size_t>(y) * l + x];
    }
    // Lähin tekseli: se, jonka alueelle (u, v) osuu.
    Vari lahin(Vec2 uv) const {
        return tekseli(static_cast<int>(std::floor(uv.x * l)),
                       static_cast<int>(std::floor(uv.y * k)));
    }
    // Bilineaarinen: neljän lähimmän tekselin keskipisteen painotettu
    // keskiarvo. Tekselin keskipiste on (i + 0.5) / l.
    Vari bilineaarinen(Vec2 uv) const {
        double x = uv.x * l - 0.5, y = uv.y * k - 0.5;
        double fx = std::floor(x), fy = std::floor(y);
        int x0 = static_cast<int>(fx), y0 = static_cast<int>(fy);
        double sx = x - fx, sy = y - fy;
        Vari yla = (1 - sx) * tekseli(x0, y0) + sx * tekseli(x0 + 1, y0);
        Vari ala = (1 - sx) * tekseli(x0, y0 + 1) +
                   sx * tekseli(x0 + 1, y0 + 1);
        return (1 - sy) * yla + sy * ala;
    }
};
// @loppu tekstuuri

// @alku shakki
inline Tekstuuri shakki(int koko, int ruutu, Vari a, Vari b) {
    Tekstuuri t{koko, koko, {}};
    for (int y = 0; y < koko; ++y)
        for (int x = 0; x < koko; ++x)
            t.t.push_back((x / ruutu + y / ruutu) % 2 ? b : a);
    return t;
}
// @loppu shakki

// @alku mipmap
// Mipmap-ketju: jokainen taso on edellisen puolikas, jokainen
// tekseli neljän tekselin keskiarvo. Tason 0 koko on kahden potenssi.
struct Mipmap {
    std::vector<Tekstuuri> tasot;

    explicit Mipmap(Tekstuuri t) {
        tasot.push_back(std::move(t));
        while (tasot.back().l > 1) {
            const Tekstuuri& e = tasot.back();
            Tekstuuri s{e.l / 2, e.k / 2, {}};
            for (int y = 0; y < s.k; ++y)
                for (int x = 0; x < s.l; ++x)
                    s.t.push_back(0.25 * (e.tekseli(2 * x, 2 * y) +
                                          e.tekseli(2 * x + 1, 2 * y) +
                                          e.tekseli(2 * x, 2 * y + 1) +
                                          e.tekseli(2 * x + 1, 2 * y + 1)));
            tasot.push_back(std::move(s));
        }
    }
    // Taso valitaan siitä, montako tekseliä yhden pikselin askel
    // ruudulla kattaa (rho). Taso log2(rho) on yksi tekseli pikselille.
    double taso(Vec2 duv_dx, Vec2 duv_dy) const {
        double l = tasot[0].l, k = tasot[0].k;
        double ax = std::hypot(duv_dx.x * l, duv_dx.y * k);
        double ay = std::hypot(duv_dy.x * l, duv_dy.y * k);
        double rho = std::max(ax, ay);
        return rho <= 1 ? 0.0 : std::log2(rho);
    }
    // Trilineaarinen: bilineaarinen kahdelta lähimmältä tasolta ja
    // niiden välillä lineaarisesti.
    Vari trilineaarinen(Vec2 uv, double lod) const {
        double maks = static_cast<double>(tasot.size() - 1);
        lod = std::clamp(lod, 0.0, maks);
        int t0 = static_cast<int>(std::floor(lod));
        int t1 = std::min(t0 + 1, static_cast<int>(maks));
        double s = lod - t0;
        return (1 - s) * tasot[t0].bilineaarinen(uv) +
               s * tasot[t1].bilineaarinen(uv);
    }
};
// @loppu mipmap
