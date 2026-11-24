// testaus.hpp: satunnaistettujen vertailutestien apuvälineet.
//
// Satunnainen on SplitMix64-generaattori (Steele, Lea ja Flood 2014),
// sama kuin Algoritmit-tutoriaalin satunnainen.h. Sama siemen antaa
// saman sarjan joka koneella. Standardikirjaston jakaumat, kuten
// std::uniform_int_distribution, voivat tuottaa eri toteutuksissa eri
// luvut, joten testidata tehdään omilla funktioilla.
//
// vaadi() on tarkistus, joka ei katoa NDEBUG-käännöksessä kuten assert.
#pragma once

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string_view>
#include <utility>
#include <vector>

class Satunnainen {
public:
    explicit Satunnainen(std::uint64_t siemen) : tila_{siemen} {}

    std::uint64_t seuraava()
    {
        std::uint64_t z = (tila_ += 0x9E3779B97F4A7C15u);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9u;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBu;
        return z ^ (z >> 31);
    }

    // Luku väliltä [0, raja), raja > 0. Jakojäännöksen vinouma on
    // testidatalle merkityksetön.
    std::uint64_t alle(std::uint64_t raja) { return seuraava() % raja; }

    // Kokonaisluku väliltä [a, b].
    int valilta(int a, int b)
    {
        auto leveys = static_cast<std::uint64_t>(b - a) + 1;
        return a + static_cast<int>(alle(leveys));
    }

    // Liukuluku väliltä [0, 1): 53 satunnaista bittiä mantissaan.
    double yksikko()
    {
        return static_cast<double>(seuraava() >> 11) * 0x1.0p-53;
    }

    // Fisher-Yates-sekoitus.
    template <class T>
    void sekoita(std::vector<T>& v)
    {
        for (std::size_t i = v.size(); i > 1; --i) {
            std::swap(v[i - 1], v[alle(i)]);
        }
    }

private:
    std::uint64_t tila_;
};

// Pysäyttää ohjelman, jos ehto ei päde. Virheilmoitus menee
// virhetulosteeseen, ja abort() jättää ytimen ja pinon tutkittaviksi.
// Puskuroitu tuloste kirjoitetaan ensin, koska abort() ei tee sitä.
inline void vaadi(bool ehto, std::string_view viesti)
{
    if (!ehto) {
        std::fflush(stdout);
        std::fprintf(stderr, "VIRHE: %.*s\n",
                     static_cast<int>(viesti.size()), viesti.data());
        std::abort();
    }
}
