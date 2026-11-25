// Bresenhamin viiva ja vertailu liukulukuversioon (DDA).
#include <cmath>
#include <cstdio>
#include <set>
#include <string>
#include <utility>
#include <vector>

#include "yhteinen/rasteri.hpp"

using Pisteet = std::set<std::pair<int, int>>;

// @alku dda
// DDA: kuljetaan pidemmän akselin suuntaan pikseli kerrallaan ja
// pyöristetään toinen koordinaatti.
Pisteet dda(int x0, int y0, int x1, int y1) {
    Pisteet p;
    int n = std::max(std::abs(x1 - x0), std::abs(y1 - y0));
    for (int i = 0; i <= n; ++i) {
        double t = n == 0 ? 0.0 : static_cast<double>(i) / n;
        p.insert({static_cast<int>(std::floor(x0 + t * (x1 - x0) + 0.5)),
                  static_cast<int>(std::floor(y0 + t * (y1 - y0) + 0.5))});
    }
    return p;
}
// @loppu dda

int main() {
    // @alku askeleet
    std::printf("viiva (0, 0) -> (7, 3):\n");
    int edellinen_y = -1;
    viiva(0, 0, 7, 3, [&](int x, int y) {
        std::printf("  (%d, %d)%s\n", x, y,
                    y != edellinen_y && x > 0 ? "  <- askel y" : "");
        edellinen_y = y;
    });
    // @loppu askeleet

    // @alku tahti
    // Viivoja keskeltä joka suuntaan; merkitään eroavat pikselit.
    const int L = 41, K = 21;
    std::vector<std::string> ruutu(K, std::string(L, ' '));
    int eroja = 0, yhteensa = 0;
    const int kohteet[][2] = {{40, 10}, {40, 0},  {30, 0}, {20, 0},
                              {7, 0},   {0, 4},   {0, 16}, {9, 20},
                              {20, 20}, {33, 20}, {40, 19}};
    for (const auto& k : kohteet) {
        Pisteet b;
        viiva(20, 10, k[0], k[1], [&](int x, int y) { b.insert({x, y}); });
        Pisteet d = dda(20, 10, k[0], k[1]);
        for (auto [x, y] : b) {
            ruutu[y][x] = d.count({x, y}) ? '#' : 'B';
            ++yhteensa;
        }
        for (auto [x, y] : d)
            if (!b.count({x, y})) ruutu[y][x] = 'D';
        eroja += static_cast<int>(b.size()) -
                 static_cast<int>(std::count_if(b.begin(), b.end(),
                     [&d](auto p) { return d.count(p) > 0; }));
    }
    for (const std::string& r : ruutu) std::printf("|%s|\n", r.c_str());
    std::printf("%d pikseliä, joista %d eri kuin DDA:lla\n", yhteensa,
                eroja);
    // @loppu tahti

#ifdef KUVITUS  // make kuvat: sama ruudukko kuvana
    Kuva kuva(L, K, {24, 24, 28});
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            char m = ruutu[static_cast<std::size_t>(y)]
                          [static_cast<std::size_t>(x)];
            if (m == '#') kuva(x, y) = {225, 225, 225};
            if (m == 'B') kuva(x, y) = {255, 150, 40};
            if (m == 'D') kuva(x, y) = {70, 160, 255};
        }
    tallenna_ppm(kuva, "03-viivat.ppm");
#endif
}
