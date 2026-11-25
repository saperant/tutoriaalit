// Väärän jakamisen hinta: säikeet kasvattavat kukin omaa laskuriaan.
// Rakenteet Tiivis ja Erillinen tulevat esimerkistä
// 10-vaara-jakaminen.cpp; tässä tiedostossa on pidempi silmukka ja
// ajastus. Mittausohjelma: ajat riippuvat koneesta, joten se ajetaan
// käsin (make tulokset) eikä kuulu testeihin.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstddef>
#include <print>
#include <thread>
#include <vector>

// Esimerkin oma main nimetään uudelleen ja jää käyttämättä; nimetty
// funktio ei saa mainin implisiittistä paluuarvoa, joten varoitus
// vaiennetaan tämän sisällytyksen ajaksi. Toinen vaiennettu varoitus
// koskee rivin koon käyttöä sisällytetyssä tiedostossa.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#pragma GCC diagnostic ignored "-Winterference-size"
#define main vaara_jakaminen_esimerkki
#include "../10-vaara-jakaminen.cpp"
#undef main
#pragma GCC diagnostic pop

namespace {

constexpr int kierroksia = 20'000'000;

// Mediaani seitsemästä ajosta millisekunteina. Säikeet odottavat
// yhteistä lähtölupaa, jotta ne ovat varmasti käynnissä yhtä aikaa.
template <class Laskuri>
double mittaa(std::size_t saikeita)
{
    std::vector<double> ajat;
    for (int toisto = 0; toisto < 7; ++toisto) {
        std::vector<Laskuri> laskurit(saikeita);
        std::atomic<bool> lahto{false};
        std::atomic<std::size_t> valmiina{0};
        std::chrono::steady_clock::time_point alku;
        {
            std::vector<std::jthread> t;
            for (std::size_t s = 0; s < saikeita; ++s) {
                t.emplace_back([&, s] {
                    valmiina.fetch_add(1);
                    while (!lahto.load(std::memory_order_acquire)) {
                    }
                    for (int i = 0; i < kierroksia; ++i) {
                        laskurit[s].n.fetch_add(
                            1, std::memory_order_relaxed);
                    }
                });
            }
            while (valmiina.load() != saikeita) {
            }
            alku = std::chrono::steady_clock::now();
            lahto.store(true, std::memory_order_release);
        }
        const std::chrono::duration<double, std::milli> kesto =
            std::chrono::steady_clock::now() - alku;
        ajat.push_back(kesto.count());
    }
    std::ranges::sort(ajat);
    return ajat[ajat.size() / 2];
}

}  // namespace

int main()
{
    std::println("omat laskurit, {} kasvatusta saietta kohden, {} ydinta",
                 kierroksia, std::thread::hardware_concurrency());
    std::println("  saikeita   tiivis (ms)   erillinen (ms)   suhde");
    for (std::size_t s : {1u, 2u, 4u}) {
        const double tiivis = mittaa<Tiivis>(s);
        const double erillinen = mittaa<Erillinen>(s);
        std::println("  {:>8}   {:>11.1f}   {:>14.1f}   {:>5.1f}", s, tiivis,
                     erillinen, tiivis / erillinen);
    }
}
