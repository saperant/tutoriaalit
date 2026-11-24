// Pikaoppaan testatut koodinpalat.
#include <cmath>
#include <cstdint>
#include <deque>
#include <print>

// @alku sekvenssi
constexpr bool uudempi(std::uint16_t a, std::uint16_t b) {
    return static_cast<std::int16_t>(static_cast<std::uint16_t>(a - b)) > 0;
}
// @loppu sekvenssi

// @alku kvantisointi
std::uint32_t kvantisoi(double x, double pienin, double suurin, int bitit) {
    const double askeleet = static_cast<double>((1u << bitit) - 1u);
    return static_cast<std::uint32_t>(
        std::lround((x - pienin) / (suurin - pienin) * askeleet));
}
// @loppu kvantisointi

// @alku puskuri
// Interpolointiviive: kaksi vedosväliä + värinän varmuusvara.
constexpr int puskuri_ms(int vedos_ms, int varina_ms) {
    return 2 * vedos_ms + varina_ms;
}
// @loppu puskuri

struct Syote {
    std::uint32_t numero;
    int suunta;
};
int liiku(int x, const Syote& s) { return x + 5 * s.suunta; }

// @alku tasmaytys
// Virallinen tila pohjaksi, kuittaamattomat syötteet uudelleen.
int tasmaa(int palvelin_x, std::uint32_t kasitelty,
           std::deque<Syote>& kesken) {
    while (!kesken.empty() && kesken.front().numero <= kasitelty) {
        kesken.pop_front();
    }
    int x = palvelin_x;
    for (const Syote& s : kesken) {
        x = liiku(x, s);
    }
    return x;
}
// @loppu tasmaytys

int main() {
    std::println("uudempi(2, 65534) = {}", uudempi(2, 65534));
    std::println("kvantisoi(1.5, 0, 10, 8) = {}", kvantisoi(1.5, 0, 10, 8));
    std::println("puskuri 20 Hz, värinä 40 ms: {} ms", puskuri_ms(50, 40));
    std::deque<Syote> kesken{{7, 1}, {8, 1}, {9, 0}};
    std::println("täsmäytetty x = {}", tasmaa(100, 7, kesken));
}
