// Mittaus, jonka kääntäjä poistaa, ja miten se estetään.
#include <cstddef>
#include <numeric>
#include <span>
#include <string_view>
#include <vector>

#include "mittari.hpp"

// @alku keskiarvo
double keskiarvo(std::span<const double> x)
{
    return std::accumulate(x.begin(), x.end(), 0.0)
           / static_cast<double>(x.size());
}
// @loppu keskiarvo

std::vector<double> luo(std::size_t n)
{
    std::vector<double> x(n);
    for (std::size_t i = 0; i < n; ++i) {
        x[i] = static_cast<double>(i % 100);
    }
    return x;
}

// @alku tavat
// Antaa funktiolle `toimi` tavan mukaisen mitattavan kierroksen.
template <typename Toimi>
void valitse(std::string_view tapa, std::span<const double> x, Toimi toimi)
{
    if (tapa == "hylatty") {
        toimi([&] { keskiarvo(x); });                  // tulos hylätään
    } else if (tapa == "pidetty") {
        toimi([&] { mittari::pida(keskiarvo(x)); });   // tulos "käytössä"
    } else if (tapa == "vakio") {
        toimi([] {
            double y[] = {1.0, 2.0, 3.0, 4.0};         // arvot tunnetaan
            mittari::pida(keskiarvo(y));
        });
    } else if (tapa == "piilotettu") {
        toimi([] {
            double y[] = {1.0, 2.0, 3.0, 4.0};
            mittari::piilota(y);                       // arvot tuntemattomia
            mittari::pida(keskiarvo(y));
        });
    }
}
// @loppu tavat

void mittaa_kaikki()
{
    std::printf("keskiarvo, 1000000 alkiota\n");
    auto x = luo(1'000'000);
    for (std::string_view tapa : {"hylatty", "pidetty"}) {
        valitse(tapa, x, [&](auto kierros) {
            mittari::tulosta(tapa, mittari::mittaa(kierros, 21));
        });
    }
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    if (tila.mittaa) {
        mittaa_kaikki();
        return 0;
    }
    auto x = luo(1000);
    if (!tila.kerran.empty()) {             // Valgrind-ajo
        valitse(tila.kerran, x, [&](auto kierros) {
            for (long i = 0; i < tila.n; ++i) {
                kierros();
            }
        });
        return 0;
    }
    std::printf("keskiarvo: %.2f\n", keskiarvo(x));
}
