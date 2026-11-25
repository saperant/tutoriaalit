// Yhteiset reunat: montako kertaa kukin pikseli piirretään?
#include <cstdio>
#include <string>
#include <vector>

#include "yhteinen/rasteri.hpp"

// @alku kolmiot
const int L = 37, K = 13;
// Kuusikulmio kuutena kolmiona ja neliö lävistäjällä jaettuna.
// Kärjet ovat pikselien keskipisteissä (x + 0.5, y + 0.5), joten
// monen pikselin keskipiste osuu täsmälleen yhteiselle reunalle.
std::vector<std::array<Vec2, 3>> kolmiot() {
    Vec2 c{12.5, 6.5};
    Vec2 kulmat[6] = {{2.5, 6.5},   {7.5, 0.5},   {17.5, 0.5},
                      {22.5, 6.5},  {17.5, 12.5}, {7.5, 12.5}};
    std::vector<std::array<Vec2, 3>> t;
    for (int i = 0; i < 6; ++i)
        t.push_back({c, kulmat[i], kulmat[(i + 1) % 6]});
    t.push_back({Vec2{26.5, 0.5}, Vec2{34.5, 0.5}, Vec2{34.5, 8.5}});
    t.push_back({Vec2{26.5, 0.5}, Vec2{34.5, 8.5}, Vec2{26.5, 8.5}});
    return t;
}
// @loppu kolmiot

// @alku laske
void laske(bool saanto) {
    std::vector<std::vector<int>> n(K, std::vector<int>(L, 0));
    for (const auto& t : kolmiot())
        rasteroi(t[0], t[1], t[2], L, K,
                 [&](int x, int y, Bary) { ++n[y][x]; }, saanto);
    int kahdesti = 0, pikseleita = 0;
    for (const auto& rivi : n) {
        std::string s;
        for (int v : rivi) {
            s += v == 0 ? '.' : static_cast<char>('0' + v);
            kahdesti += v > 1;
            pikseleita += v > 0;
        }
        std::printf("|%s|\n", s.c_str());
    }
    std::printf("%s: %d pikseliä, joista %d useammin kuin kerran\n\n",
                saanto ? "vasen-ylä-sääntö" : "reuna mukaan (>= 0)",
                pikseleita, kahdesti);
}
// @loppu laske

int main() {
    laske(false);
    laske(true);

#ifdef KUVITUS  // make kuvat: piirtokerrat väreinä, ylhäällä ilman sääntöä
    Kuva kuva(L, 2 * K + 1, {24, 24, 28});
    for (int osa = 0; osa < 2; ++osa) {
        std::vector<std::vector<int>> n(K, std::vector<int>(L, 0));
        for (const auto& t : kolmiot())
            rasteroi(t[0], t[1], t[2], L, K,
                     [&](int x, int y, Bary) {
                         ++n[static_cast<std::size_t>(y)]
                            [static_cast<std::size_t>(x)];
                     },
                     osa == 1);
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x) {
                int v = n[static_cast<std::size_t>(y)]
                         [static_cast<std::size_t>(x)];
                if (v == 1) kuva(x, osa * (K + 1) + y) = {200, 200, 200};
                if (v == 2) kuva(x, osa * (K + 1) + y) = {255, 160, 40};
                if (v > 2) kuva(x, osa * (K + 1) + y) = {230, 50, 50};
            }
    }
    tallenna_ppm(kuva, "04-peitto.ppm");
#endif
}
