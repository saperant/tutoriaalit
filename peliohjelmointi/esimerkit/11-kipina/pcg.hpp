// PCG32-satunnaislukugeneraattori (ks. luku Pelisilmukka).
#pragma once
#include <cstdint>

class Pcg32 {
public:
    explicit Pcg32(std::uint64_t siemen, std::uint64_t virta = 54)
        : lisays_((virta << 1u) | 1u) {
        seuraava();
        tila_ += siemen;
        seuraava();
    }
    std::uint32_t seuraava() {
        const std::uint64_t vanha = tila_;
        tila_ = vanha * 6364136223846793005ULL + lisays_;
        const auto x =
            static_cast<std::uint32_t>(((vanha >> 18u) ^ vanha) >> 27u);
        const auto k = static_cast<std::uint32_t>(vanha >> 59u);
        return (x >> k) | (x << ((32u - k) & 31u));
    }
    // Liukuluku välillä [a, b).
    double valilta(double a, double b) {
        return a + (b - a) * (seuraava() >> 8) * (1.0 / (1u << 24));
    }

private:
    std::uint64_t tila_ = 0;
    std::uint64_t lisays_;
};
