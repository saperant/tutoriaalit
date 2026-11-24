// Lajittelu vertailijalla, joka on toisessa käännösyksikössä.
#include <algorithm>
#include <cstdio>
#include <string_view>
#include <vector>

#include "../mittari.hpp"
#include "../satunnainen.hpp"
#include "tuote.hpp"

std::vector<Tuote> luo(int n)
{
    Satunnainen s{5};
    std::vector<Tuote> t;
    for (int i = 0; i < n; ++i) {
        t.push_back({i, static_cast<int>(s.alle(100000))});
    }
    return t;
}

// @alku lajittelu
// Vertailu on toisessa käännösyksikössä: ilman LTO:ta jokainen
// vertailu on funktiokutsu.
[[gnu::noinline]] void lajittele_erillinen(std::vector<Tuote>& t)
{
    std::ranges::sort(t, [](const Tuote& a, const Tuote& b) {
        return hinta_ensin_erillinen(a, b);
    });
}

// Otsakkeen inline-funktio: vertailu sisällytetään aina.
[[gnu::noinline]] void lajittele_inline(std::vector<Tuote>& t)
{
    std::ranges::sort(t, [](const Tuote& a, const Tuote& b) {
        return hinta_ensin(a, b);
    });
}
// @loppu lajittelu

template <typename Toimi>
void valitse(std::string_view tapa, const std::vector<Tuote>& alku,
             Toimi toimi)
{
    if (tapa == "erillinen") {
        toimi([&] {
            auto k = alku;
            lajittele_erillinen(k);
            mittari::pida(k.front());
        });
    } else if (tapa == "inline") {
        toimi([&] {
            auto k = alku;
            lajittele_inline(k);
            mittari::pida(k.front());
        });
    }
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    if (tila.mittaa) {
        auto alku = luo(1'000'000);
        std::printf("lajittelu hinnan mukaan, 1000000 tuotetta\n");
        for (std::string_view tapa : {"erillinen", "inline"}) {
            valitse(tapa, alku, [&](auto f) {
                mittari::tulosta(tapa, mittari::mittaa(f, 11));
            });
        }
        return 0;
    }
    auto t = luo(1000);
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, t, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    auto u = t;
    lajittele_erillinen(t);
    lajittele_inline(u);
    bool samat = std::ranges::equal(
        t, u, [](const Tuote& a, const Tuote& b) {
            return a.hinta_snt == b.hinta_snt;
        });
    std::printf("halvin %d snt, kallein %d snt, jarjestykset samat: %s\n",
                t.front().hinta_snt, t.back().hinta_snt,
                samat ? "kylla" : "ei");
}
