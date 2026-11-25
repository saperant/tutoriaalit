// Rinnakkaisen reduktion nopeutus säiemäärän funktiona. Mitattava koodi
// on esimerkin 10-reduktio.cpp funktio sellaisenaan; tässä tiedostossa
// on vain ajastus. Mittausohjelma: ajat riippuvat koneesta, joten se
// ajetaan käsin (make tulokset) eikä kuulu testeihin.
#include <algorithm>
#include <chrono>
#include <cstddef>
#include <print>
#include <thread>
#include <vector>

// Esimerkin oma main nimetään uudelleen ja jää käyttämättä; nimetty
// funktio ei saa mainin implisiittistä paluuarvoa, joten varoitus
// vaiennetaan tämän sisällytyksen ajaksi.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main reduktio_esimerkki
#include "../10-reduktio.cpp"
#undef main
#pragma GCC diagnostic pop

namespace {

// Mediaani yhdeksästä ajosta millisekunteina.
template <class Summain>
double mittaa(const std::vector<double>& x, std::size_t saikeita)
{
    std::vector<double> ajat;
    volatile double nielu = 0.0;
    for (int toisto = 0; toisto < 9; ++toisto) {
        const auto alku = std::chrono::steady_clock::now();
        nielu = rinnakkainen_summa<Summain>(x, saikeita);
        const std::chrono::duration<double, std::milli> kesto =
            std::chrono::steady_clock::now() - alku;
        ajat.push_back(kesto.count());
    }
    (void)nielu;
    std::ranges::sort(ajat);
    return ajat[ajat.size() / 2];
}

template <class Summain>
void taulukko(const char* nimi, const std::vector<double>& x)
{
    std::println("{}", nimi);
    std::println("  saikeita   aika (ms)   nopeutus");
    const double yksi = mittaa<Summain>(x, 1);
    for (std::size_t s : {1u, 2u, 3u, 4u, 8u}) {
        const double aika = s == 1 ? yksi : mittaa<Summain>(x, s);
        std::println("  {:>8}   {:>9.1f}   {:>8.2f}", s, aika, yksi / aika);
    }
}

}  // namespace

int main()
{
    std::vector<double> x(40'000'000);
    for (std::size_t i = 0; i < x.size(); ++i) {
        x[i] = 1.0 / static_cast<double>(i + 1);
    }
    std::println("rinnakkainen summa, {} lukua, {} ydinta", x.size(),
                 std::thread::hardware_concurrency());
    taulukko<Kahan>("Kahan-summa (nelja laskutoimitusta alkiota kohden)",
                    x);
    taulukko<Tavallinen>("tavallinen summa (yksi yhteenlasku)", x);
}
