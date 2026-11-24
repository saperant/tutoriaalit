// Satunnaisluvut: PCG32 ja Haltonin jono.
#pragma once
#include <cstdint>

// @alku pcg
// PCG32 (O'Neill 2014): 64-bittinen tila, 32-bittinen tulos. Sama
// siemen antaa saman jonon kaikilla kääntäjillä ja alustoilla, toisin
// kuin std::uniform_real_distribution, jonka algoritmia standardi ei
// määrää. Jono-parametri valitsee toisistaan riippumattoman virran.
class Pcg32 {
public:
    explicit Pcg32(std::uint64_t siemen, std::uint64_t jono = 0)
        : lisa_((jono << 1u) | 1u) {
        seuraava();
        tila_ += siemen;
        seuraava();
    }
    std::uint32_t seuraava() {
        std::uint64_t vanha = tila_;
        tila_ = vanha * 6364136223846793005ULL + lisa_;
        auto xs = static_cast<std::uint32_t>(((vanha >> 18u) ^ vanha) >> 27u);
        auto kierto = static_cast<std::uint32_t>(vanha >> 59u);
        return (xs >> kierto) | (xs << ((32u - kierto) & 31u));
    }
    // Tasajakauma välillä [0, 1).
    double tasainen() { return seuraava() * 0x1p-32; }

private:
    std::uint64_t tila_ = 0, lisa_;
};
// @loppu pcg

// @alku halton
// Haltonin jonon i:s alkio kannassa b: luvun i numerot kannassa b
// peilattuna desimaalipilkun toiselle puolelle (radical inverse).
inline double halton(std::uint32_t i, std::uint32_t b) {
    double tulos = 0, f = 1.0 / b;
    while (i > 0) {
        tulos += f * (i % b);
        i /= b;
        f /= b;
    }
    return tulos;
}
// @loppu halton
