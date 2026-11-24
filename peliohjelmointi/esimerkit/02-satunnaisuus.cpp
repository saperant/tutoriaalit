// Toistettava satunnaisuus: oma PCG32-generaattori ja välin valinta,
// jotka tuottavat saman sarjan kaikilla alustoilla ja kääntäjillä.
#include <array>
#include <cstdint>
#include <print>

// @alku pcg
// PCG32 (O'Neill 2014): 64-bittinen tila, 32-bittinen tulos.
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
        const auto xorattu =
            static_cast<std::uint32_t>(((vanha >> 18u) ^ vanha) >> 27u);
        const auto kierto = static_cast<std::uint32_t>(vanha >> 59u);
        return (xorattu >> kierto) | (xorattu << ((32u - kierto) & 31u));
    }

    // Tasainen kokonaisluku välillä [0, raja) ilman vinoumaa.
    std::uint32_t valilta(std::uint32_t raja) {
        const std::uint32_t kynnys = (0u - raja) % raja;
        for (;;) {
            const std::uint32_t r = seuraava();
            if (r >= kynnys) {
                return r % raja;
            }
        }
    }

private:
    std::uint64_t tila_ = 0;
    std::uint64_t lisays_;
};
// @loppu pcg

int main() {
    Pcg32 a(42), b(42), c(43);
    std::print("siemen 42:");
    for (int i = 0; i < 4; ++i) {
        std::print(" {}", a.seuraava());
    }
    std::print("\nsiemen 42:");
    for (int i = 0; i < 4; ++i) {
        std::print(" {}", b.seuraava());
    }
    std::print("\nsiemen 43:");
    for (int i = 0; i < 4; ++i) {
        std::print(" {}", c.seuraava());
    }
    std::println();

    // @alku noppa
    Pcg32 noppa(2026);
    std::array<int, 6> maarat{};
    for (int i = 0; i < 60'000; ++i) {
        ++maarat[noppa.valilta(6)];
    }
    // @loppu noppa
    for (int i = 0; i < 6; ++i) {
        std::println("silmäluku {}: {}", i + 1, maarat[i]);
    }
}
