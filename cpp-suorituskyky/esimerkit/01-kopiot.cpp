// Huomaamattomat kopiot: silmukkamuuttuja ja parametri arvona.
#include <cstddef>
#include <format>
#include <string>
#include <vector>

#include "laskuri.hpp"
#include "mittari.hpp"

// @alku hidas
// Laskee nimien yhteispituuden. Silmukkamuuttuja on arvo, joten
// jokainen nimi kopioidaan, ja pitkän nimen kopio varaa muistia.
// Myös parametri on arvo: koko vektori kopioidaan kutsussa.
std::size_t pituudet_hidas(std::vector<std::string> nimet)
{
    std::size_t yhteensa = 0;
    for (auto nimi : nimet) {
        yhteensa += nimi.size();
    }
    return yhteensa;
}
// @loppu hidas

// @alku nopea
std::size_t pituudet(const std::vector<std::string>& nimet)
{
    std::size_t yhteensa = 0;
    for (const auto& nimi : nimet) {
        yhteensa += nimi.size();
    }
    return yhteensa;
}
// @loppu nopea

std::vector<std::string> luo_nimet(std::size_t n)
{
    std::vector<std::string> nimet;
    nimet.reserve(n);
    for (std::size_t i = 0; i < n; ++i) {
        nimet.push_back(std::format("asiakas-{:06}@esimerkki.fi", i));
    }
    return nimet;
}

void mittaa_kaikki()
{
    std::printf("nimien yhteispituus, 100000 nimea\n");
    auto nimet = luo_nimet(100000);
    auto th = mittari::mittaa([&] {
        mittari::pida(pituudet_hidas(nimet));
    }, 21);
    auto tn = mittari::mittaa([&] {
        mittari::pida(pituudet(nimet));
    }, 21);
    mittari::tulosta("arvona (kopiot)", th);
    mittari::tulosta("viittauksena", tn, th.mediaani_ms);
}

int main(int argc, char** argv)
{
    if (mittari::lue_tila({argv, static_cast<std::size_t>(argc)}).mittaa) {
        mittaa_kaikki();
        return 0;
    }
    // @alku testi
    auto nimet = luo_nimet(1000);
    laskuri::Jakso hidas;
    std::size_t a = pituudet_hidas(nimet);
    std::size_t varaukset_hidas = hidas.varaukset();
    laskuri::Jakso nopea;
    std::size_t b = pituudet(nimet);
    std::size_t varaukset_nopea = nopea.varaukset();
    std::printf("pituudet: %zu ja %zu\n", a, b);
    std::printf("varauksia: arvona %zu, viittauksena %zu\n",
                varaukset_hidas, varaukset_nopea);
    // @loppu testi
}
