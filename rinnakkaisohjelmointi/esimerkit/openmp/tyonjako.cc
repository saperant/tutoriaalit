// OpenMP: reduktio ja työnjako kääntäjän direktiiveillä. Käännetään
// valitsimella -fopenmp; ilman sitä direktiivit ohitetaan ja ohjelma
// on sarjallinen. Sama kuorma kuin esimerkissä 10-tyonjako.cpp.
#include <omp.h>

#include <algorithm>
#include <array>
#include <cstdint>
#include <numeric>
#include <print>

constexpr int tehtavia = 4'000;
constexpr int saikeita = 4;

// Suurin säiekohtainen kuorma suhteessa keskiarvoon.
double epatasapaino(const std::array<std::int64_t, saikeita>& kuorma)
{
    const auto summa = std::reduce(kuorma.begin(), kuorma.end());
    return static_cast<double>(std::ranges::max(kuorma)) * saikeita /
           static_cast<double>(summa);
}

int main()
{
    // @alku reduktio
    // Jokainen säie saa oman kopionsa muuttujasta summa, ja kopiot
    // yhdistetään silmukan lopussa.
    std::int64_t summa = 0;
    #pragma omp parallel for num_threads(saikeita) reduction(+ : summa)
    for (int i = 1; i <= 1'000'000; ++i) {
        summa += i;
    }
    std::println("summa {}", summa);
    // @loppu reduktio

    // @alku jako
    // Tehtävän i hinta on i + 1 yksikköä. Jokainen säie kirjaa oman
    // kuormansa omaan alkioonsa.
    std::array<std::int64_t, saikeita> kuorma{};
    #pragma omp parallel for num_threads(saikeita) schedule(static)
    for (int i = 0; i < tehtavia; ++i) {
        kuorma[omp_get_thread_num()] += i + 1;
    }
    std::println("schedule(static): suurin/keskiarvo {:.2f}",
                 epatasapaino(kuorma));

    kuorma = {};
    #pragma omp parallel for num_threads(saikeita) schedule(static, 1)
    for (int i = 0; i < tehtavia; ++i) {
        kuorma[omp_get_thread_num()] += i + 1;
    }
    std::println("schedule(static, 1): suurin/keskiarvo {:.2f}",
                 epatasapaino(kuorma));

    kuorma = {};
    #pragma omp parallel for num_threads(saikeita) schedule(dynamic, 32)
    for (int i = 0; i < tehtavia; ++i) {
        kuorma[omp_get_thread_num()] += i + 1;
    }
    std::println("schedule(dynamic, 32): kaikki tehty {}",
                 std::reduce(kuorma.begin(), kuorma.end()) ==
                     std::int64_t{tehtavia} * (tehtavia + 1) / 2
                     ? "kylla" : "ei");
    // @loppu jako
}
