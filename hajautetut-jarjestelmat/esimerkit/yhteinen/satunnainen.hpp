// Toistettava satunnaislukugeneraattori (PCG32, O'Neill 2014).
//
// Standardikirjaston jakaumat (std::uniform_int_distribution ym.)
// antavat eri toteutuksissa eri lukuja samalla siemenellä, joten
// simulaattori käyttää omaa generaattoria ja omia muunnoksia.
#pragma once
#include <cstdint>

class Satunnainen {
public:
    explicit Satunnainen(std::uint64_t siemen, std::uint64_t virta = 54)
        : tila_(0), lisa_((virta << 1u) | 1u) {
        seuraava();
        tila_ += siemen;
        seuraava();
    }

    std::uint32_t seuraava() {
        std::uint64_t vanha = tila_;
        tila_ = vanha * 6364136223846793005ULL + lisa_;
        auto xs = static_cast<std::uint32_t>(((vanha >> 18u) ^ vanha)
                                             >> 27u);
        auto kierto = static_cast<std::uint32_t>(vanha >> 59u);
        return (xs >> kierto) | (xs << ((-kierto) & 31u));
    }

    // @alku muunnos
    // Tasainen kokonaisluku väliltä [a, b] ilman modulon vinoumaa.
    std::int64_t valilta(std::int64_t a, std::int64_t b) {
        auto n = static_cast<std::uint64_t>(b - a) + 1;
        std::uint64_t raja = (0x1'0000'0000ULL / n) * n;
        std::uint64_t x;
        do {
            x = seuraava();
        } while (x >= raja);
        return a + static_cast<std::int64_t>(x % n);
    }

    // Tapahtuuko asia, jonka todennäköisyys on promillea / 1000.
    bool tapahtuu(int promillea) { return valilta(0, 999) < promillea; }
    // @loppu muunnos

private:
    std::uint64_t tila_, lisa_;
};
