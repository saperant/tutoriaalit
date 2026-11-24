// TSAN
// Työnjako epätasaiselle kuormalle: tehtävän i hinta kasvaa i:n mukana.
// Staattinen yhtenäinen jako, syklinen jako ja dynaaminen jako
// atomisella laskurilla.
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <functional>
#include <print>
#include <string_view>
#include <thread>
#include <vector>

constexpr std::size_t tehtavia = 4'000;
constexpr std::size_t saikeita = 4;

// "Työ": tehtävän i hinta on i + 1 yksikköä.
std::uint64_t tee(std::size_t i)
{
    std::uint64_t x = i;
    for (std::size_t k = 0; k <= i; ++k) {
        x = x * 6364136223846793005u + 1;
    }
    return x >> 60;
}

using Jakaja = std::function<void(std::size_t s,
                                  const std::function<void(std::size_t)>&)>;

void aja(std::string_view nimi, const Jakaja& jako, bool deterministinen)
{
    std::vector<std::uint64_t> yksikot(saikeita, 0);
    std::vector<std::atomic<int>> tehty(tehtavia);
    {
        std::vector<std::jthread> t;
        for (std::size_t s = 0; s < saikeita; ++s) {
            t.emplace_back([&, s] {
                std::uint64_t oma = 0;
                jako(s, [&](std::size_t i) {
                    (void)tee(i);
                    oma += i + 1;
                    tehty[i].fetch_add(1, std::memory_order_relaxed);
                });
                yksikot[s] = oma;
            });
        }
    }
    const bool kerran = std::ranges::all_of(
        tehty, [](const std::atomic<int>& n) { return n.load() == 1; });
    const std::uint64_t suurin = std::ranges::max(yksikot);
    std::uint64_t summa = 0;
    for (auto y : yksikot) {
        summa += y;
    }
    // Epätasapaino: suurin kuorma suhteessa keskiarvoon.
    const double epatasapaino = static_cast<double>(suurin) * saikeita /
                                static_cast<double>(summa);
    std::print(stderr, "{}: suurin/keskiarvo {:.2f}\n", nimi, epatasapaino);
    if (deterministinen) {
        std::println("{}: jokainen kerran {}, suurin/keskiarvo {:.2f}",
                     nimi, kerran ? "kylla" : "ei", epatasapaino);
    } else {
        std::println("{}: jokainen kerran {}", nimi,
                     kerran ? "kylla" : "ei");
    }
}

int main()
{
    // @alku jaot
    // Yhtenäiset palat: säie s saa välin [s*n/p, (s+1)*n/p).
    aja("staattinen", [](std::size_t s, const auto& tyo) {
        for (std::size_t i = s * tehtavia / saikeita;
             i < (s + 1) * tehtavia / saikeita; ++i) {
            tyo(i);
        }
    }, true);
    // Syklinen: säie s saa tehtävät s, s+p, s+2p, ...
    aja("syklinen", [](std::size_t s, const auto& tyo) {
        for (std::size_t i = s; i < tehtavia; i += saikeita) {
            tyo(i);
        }
    }, true);
    // Dynaaminen: vapaa säie hakee seuraavan 32 tehtävän erän.
    std::atomic<std::size_t> seuraava{0};
    aja("dynaaminen", [&seuraava](std::size_t, const auto& tyo) {
        for (;;) {
            const std::size_t alku = seuraava.fetch_add(32);
            if (alku >= tehtavia) {
                return;
            }
            for (std::size_t i = alku;
                 i < std::min(alku + 32, tehtavia); ++i) {
                tyo(i);
            }
        }
    }, false);
    // @loppu jaot
}
