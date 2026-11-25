// TSAN
// Standardikirjaston rinnakkaiset algoritmit: suorituspolitiikka on
// lupa rinnakkaistaa, ei käsky. Tulos ei saa riippua järjestyksestä.
//
// libstdc++ valitsee TBB-taustan, jos TBB:n otsakkeet löytyvät, ja silloin
// ohjelma pitää linkittää valitsimella -ltbb. Esimerkki valitsee
// sarjallisen taustan itse, jotta se kääntyy samoin joka koneella.
#define _GLIBCXX_USE_TBB_PAR_BACKEND 0
#include <algorithm>
#include <cstdint>
#include <execution>
#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main()
{
    // @alku politiikat
    std::vector<std::uint64_t> luvut(1'000'000);
    std::iota(luvut.begin(), luvut.end(), 1u);

    // reduce saa laskea summan missä järjestyksessä tahansa, joten
    // operaation on oltava liitännäinen ja vaihdannainen.
    const auto summa = std::reduce(std::execution::par, luvut.begin(),
                                   luvut.end(), std::uint64_t{0});

    // transform_reduce: neliöiden summa ilman välitaulukkoa.
    const auto neliot = std::transform_reduce(
        std::execution::par, luvut.begin(), luvut.end(),
        std::uint64_t{0}, std::plus<>{},
        [](std::uint64_t x) { return x * x % 1'000'003; });

    // Lajittelu ja haku rinnakkaispolitiikalla.
    std::vector<std::uint64_t> sekaisin(luvut.rbegin(), luvut.rend());
    std::sort(std::execution::par, sekaisin.begin(), sekaisin.end());
    const bool samat = std::equal(std::execution::par, sekaisin.begin(),
                                  sekaisin.end(), luvut.begin());

    // par_unseq sallii myös vektoroinnin: funktio ei saa lukita eikä
    // varata muistia.
    std::vector<double> puolikkaat(luvut.size());
    std::transform(std::execution::par_unseq, luvut.begin(), luvut.end(),
                   puolikkaat.begin(), [](std::uint64_t x) {
                       return static_cast<double>(x) * 0.5;
                   });
    // @loppu politiikat
    std::println("summa {}", summa);
    std::println("nelioiden jaannosten summa {}", neliot);
    std::println("lajittelu oikein: {}", samat ? "kylla" : "ei");
    std::println("viimeinen puolikas {}", puolikkaat.back());
}
