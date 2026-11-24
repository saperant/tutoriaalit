// Testidata ja vertailu CPU-referenssiin. Satunnaisluvut tulevat
// kiinteästä siemenestä, joten jokainen ajo käsittelee samaa dataa.
#pragma once

#include <cmath>
#include <cstdint>
#include <cstring>
#include <span>
#include <string_view>

// SplitMix64: pieni, nopea ja kaikilla alustoilla sama generaattori.
class Satunnainen {
public:
    explicit Satunnainen(std::uint64_t siemen) : tila_{siemen} {}
    std::uint64_t seuraava() {
        std::uint64_t z = (tila_ += 0x9E3779B97F4A7C15ull);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
        return z ^ (z >> 31);
    }
    std::uint32_t u32() { return static_cast<std::uint32_t>(seuraava()); }
    // Tasajakauma välillä [0, 1) 24 bitin tarkkuudella.
    float f32() {
        return static_cast<float>(seuraava() >> 40) * 0x1.0p-24f;
    }

private:
    std::uint64_t tila_;
};

// @alku vertaa
// Kokonaisluvut vertaillaan tarkasti: montako alkiota eroaa.
template <typename T>
std::size_t eroavia(std::span<const T> a, std::span<const T> b) {
    std::size_t n = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        n += a[i] != b[i] ? 1 : 0;
    }
    return n;
}

// Liukuluvut: suurin suhteellinen ero. Nimittäjä ei laske alle
// arvon 1, jotta nollan lähellä vertailu on absoluuttinen.
inline double suurin_ero(std::span<const float> a,
                         std::span<const float> b) {
    double suurin = 0.0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        const double ero = std::abs(static_cast<double>(a[i]) - b[i]);
        const double mittakaava =
            std::fmax(1.0, std::abs(static_cast<double>(b[i])));
        suurin = std::fmax(suurin, ero / mittakaava);
    }
    return suurin;
}
// @loppu vertaa

inline const char* kylla(bool b) { return b ? "kylla" : "ei"; }

// Esimerkit ajetaan testeissä ilman argumentteja. Argumentti --mittaa
// lisää ajat, jotka vaihtelevat koneittain eikä niitä verrata.
inline bool mittaustila(int argc, char** argv) {
    return argc > 1 && std::string_view{argv[1]} == "--mittaa";
}
