// TSAN
// Rinnakkainen prefiksisumma kolmessa vaiheessa: lohkojen omat summat,
// lohkosummien prefiksi ja siirtymän lisääminen lohkoihin.
#include <barrier>
#include <cstddef>
#include <cstdint>
#include <numeric>
#include <print>
#include <thread>
#include <vector>

// @alku prefiksi
void rinnakkainen_prefiksi(std::vector<std::uint64_t>& x,
                           std::size_t lohkoja)
{
    std::vector<std::uint64_t> siirtyma(lohkoja, 0);
    // Valmistumisfunktio ajetaan kerran, kun kaikki lohkot ovat
    // saaneet vaiheen 1 valmiiksi: lohkosummista eksklusiivinen prefiksi.
    std::barrier este{static_cast<std::ptrdiff_t>(lohkoja),
                      [&]() noexcept {
                          std::exclusive_scan(siirtyma.begin(),
                                              siirtyma.end(),
                                              siirtyma.begin(),
                                              std::uint64_t{0});
                      }};
    std::vector<std::jthread> saikeet;
    for (std::size_t b = 0; b < lohkoja; ++b) {
        saikeet.emplace_back([&x, &siirtyma, &este, b, lohkoja] {
            const auto alku = x.begin() + static_cast<std::ptrdiff_t>(
                                  b * x.size() / lohkoja);
            const auto loppu = x.begin() + static_cast<std::ptrdiff_t>(
                                   (b + 1) * x.size() / lohkoja);
            std::inclusive_scan(alku, loppu, alku);           // vaihe 1
            siirtyma[b] = alku == loppu ? 0 : *(loppu - 1);
            este.arrive_and_wait();                           // vaihe 2
            for (auto it = alku; it != loppu; ++it) {         // vaihe 3
                *it += siirtyma[b];
            }
        });
    }
}   // saikeet puretaan ensin (määritelty viimeisenä): join ennen paluuta
// @loppu prefiksi

int main()
{
    // @alku kaytto
    std::vector<std::uint64_t> x(1'000'001);
    for (std::size_t i = 0; i < x.size(); ++i) {
        x[i] = (i * 37) % 101;
    }
    std::vector<std::uint64_t> odotettu(x.size());
    std::inclusive_scan(x.begin(), x.end(), odotettu.begin());
    for (std::size_t lohkoja : {1u, 2u, 3u, 4u}) {
        auto y = x;
        rinnakkainen_prefiksi(y, lohkoja);
        std::println("{} lohkoa: viimeinen {}, sama kuin sarjassa: {}",
                     lohkoja, y.back(), y == odotettu ? "kylla" : "ei");
    }
    // @loppu kaytto
}
