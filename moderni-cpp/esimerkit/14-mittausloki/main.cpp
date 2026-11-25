// main.cpp: käyttäjä näkee vain otsikkotiedoston rajapinnan.
#include <limits>
#include <print>
#include <stdexcept>
#include <utility>
#include <vector>

#include "mittausloki.hpp"

namespace mittaus = tutoriaali::mittaus;

int main()
{
    mittaus::Mittausloki loki{"lämpötila"};
    for (double t : {21.5, 22.0, 19.5, 23.0}) {
        loki.lisaa(t);
    }
    try {
        loki.lisaa(std::numeric_limits<double>::quiet_NaN());
    } catch (const std::invalid_argument& e) {
        std::println("hylätty: {}", e.what());
    }

    std::vector<mittaus::Mittausloki> lokit;
    lokit.push_back(std::move(loki));   // siirto: toteutus vaihtaa omistajaa

    const auto y = lokit.front().yhteenveto();
    std::println("{}: {} arvoa, {:.1f}...{:.1f}, keskiarvo {:.2f}",
                 lokit.front().nimi(), y.maara, y.pienin, y.suurin,
                 y.keskiarvo);
}
