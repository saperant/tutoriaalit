// Bittitason pakkaus ja kvantisointi: kentät kirjoitetaan juuri niin
// moneen bittiin kuin pelin tarkkuus vaatii.
#include <cmath>
#include <cstdint>
#include <print>
#include <vector>

// @alku kirjoittaja
class BittiKirjoittaja {
public:
    void kirjoita(std::uint32_t arvo, int bitit) {
        for (int i = bitit - 1; i >= 0; --i) {
            if (bitti_ % 8 == 0) {
                tavut_.push_back(0);
            }
            const auto b = static_cast<std::uint8_t>((arvo >> i) & 1u);
            tavut_.back() |= static_cast<std::uint8_t>(b << (7 - bitti_ % 8));
            ++bitti_;
        }
    }
    const std::vector<std::uint8_t>& tavut() const { return tavut_; }
    int bitit() const { return bitti_; }

private:
    std::vector<std::uint8_t> tavut_;
    int bitti_ = 0;
};

class BittiLukija {
public:
    explicit BittiLukija(const std::vector<std::uint8_t>& tavut)
        : tavut_(tavut) {}
    std::uint32_t lue(int bitit) {
        std::uint32_t arvo = 0;
        for (int i = 0; i < bitit; ++i, ++bitti_) {
            const auto b = (tavut_.at(bitti_ / 8) >> (7 - bitti_ % 8)) & 1;
            arvo = (arvo << 1) | static_cast<std::uint32_t>(b);
        }
        return arvo;
    }

private:
    const std::vector<std::uint8_t>& tavut_;
    int bitti_ = 0;
};
// @loppu kirjoittaja

// @alku kvantisointi
// Arvo välillä [pienin, suurin] kokonaisluvuksi, jossa on 'bitit' bittiä.
std::uint32_t kvantisoi(double x, double pienin, double suurin, int bitit) {
    const double askeleet = static_cast<double>((1u << bitit) - 1u);
    const double s = std::lround((x - pienin) / (suurin - pienin) * askeleet);
    return static_cast<std::uint32_t>(s);
}
double palauta(std::uint32_t q, double pienin, double suurin, int bitit) {
    const double askeleet = static_cast<double>((1u << bitit) - 1u);
    return pienin + q * (suurin - pienin) / askeleet;
}
// @loppu kvantisointi

struct Pelaaja {
    double x, y;       // metriä, kartta -512..512
    double suunta;     // asteita 0..360
    int terveys;       // 0..100
    bool kyykyssa;
};

int main() {
    // @alku pakkaus
    const Pelaaja p{123.456, -78.901, 271.3, 87, true};
    BittiKirjoittaja k;
    k.kirjoita(kvantisoi(p.x, -512, 512, 17), 17);  // 1/128 m tarkkuus
    k.kirjoita(kvantisoi(p.y, -512, 512, 17), 17);
    k.kirjoita(kvantisoi(p.suunta, 0, 360, 9), 9);  // alle 1 asteen
    k.kirjoita(static_cast<std::uint32_t>(p.terveys), 7);
    k.kirjoita(p.kyykyssa ? 1u : 0u, 1);
    // @loppu pakkaus
    std::println("naiivi rakenne: {} tavua, pakattu: {} bittiä = {} tavua",
                 3 * sizeof(float) + sizeof(int) + sizeof(bool) + 3,
                 k.bitit(), k.tavut().size());

    BittiLukija l(k.tavut());
    const double x = palauta(l.lue(17), -512, 512, 17);
    const double y = palauta(l.lue(17), -512, 512, 17);
    const double suunta = palauta(l.lue(9), 0, 360, 9);
    const auto terveys = l.lue(7);
    const auto kyykyssa = l.lue(1);
    std::println("x {:.3f} (virhe {:.4f} m), y {:.3f} (virhe {:.4f} m)", x,
                 std::abs(x - p.x), y, std::abs(y - p.y));
    std::println("suunta {:.2f} (virhe {:.2f}°), terveys {}, kyykyssä {}",
                 suunta, std::abs(suunta - p.suunta), terveys, kyykyssa);
}
