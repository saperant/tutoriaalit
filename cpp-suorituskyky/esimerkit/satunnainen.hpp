// satunnainen.hpp: pieni toistettava satunnaislukugeneraattori.
//
// SplitMix64 (Steele, Lea ja Flood 2014). Standardikirjaston jakaumat
// (esim. std::uniform_int_distribution) voivat antaa eri toteutuksissa
// eri luvut, joten testit käyttävät omaa, kaikkialla samaa muunnosta.
#ifndef SATUNNAINEN_HPP
#define SATUNNAINEN_HPP

#include <cstdint>

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

    // Tasajakautunut luku väliltä [0, raja); pieni vinouma ei haittaa.
    std::uint32_t alle(std::uint32_t raja)
    {
        return static_cast<std::uint32_t>(seuraava() % raja);
    }

private:
    std::uint64_t tila_;
};

#endif
