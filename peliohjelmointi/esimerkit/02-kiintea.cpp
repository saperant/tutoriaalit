// Kiinteä aika-askel: simulaatio etenee samoin askelin, vaikka
// ruutujen kesto vaihtelee. Aika lasketaan kokonaislukuina.
#include <algorithm>
#include <chrono>
#include <print>
#include <vector>

using namespace std::chrono_literals;
using Kesto = std::chrono::nanoseconds;

struct Tila {
    double y = 0.0;
    double vy = 5.0;
    int askelia = 0;
};

void askel(Tila& t, double dt) {
    t.vy -= 9.81 * dt;  // semi-implisiittinen Euler (luku 8)
    t.y += t.vy * dt;
    ++t.askelia;
}

// @alku kertyma
constexpr Kesto ASKEL = 1'000'000'000ns / 60;  // 1/60 s
constexpr Kesto MAKSIMI = 250ms;                // kuolemanspiraalin esto

Tila aja(const std::vector<Kesto>& ruutujen_kestot) {
    const double dt = std::chrono::duration<double>(ASKEL).count();
    Tila tila;
    Kesto kertyma{0};
    for (Kesto kesto : ruutujen_kestot) {
        kertyma += std::min(kesto, MAKSIMI);
        while (kertyma >= ASKEL) {
            askel(tila, dt);
            kertyma -= ASKEL;
        }
        // Piirto tähän: alfa = kertyma / ASKEL (ks. interpolointi).
    }
    return tila;
}
// @loppu kertyma

int main(int argc, char**) {
    // Kolme koneen eri tahtia; jokainen kestää yhteensä 0,9 sekuntia.
    std::vector<Kesto> tasainen(90, 10ms);
    std::vector<Kesto> nykiva;
    for (int i = 0; i < 30; ++i) {
        nykiva.insert(nykiva.end(), {5ms, 20ms, 5ms});
    }
    if (argc > 1) {  // käyrätila kuvitusta varten: askelia ruuduittain
        for (std::size_t n = 1; n <= 15; ++n) {
            const std::vector<Kesto> alku(nykiva.begin(),
                                          nykiva.begin() + n);
            std::println("{} {} {}", n, nykiva[n - 1].count(),
                         aja(alku).askelia);
        }
        return 0;
    }
    std::vector<Kesto> hidas(9, 100ms);

    for (const auto& [nimi, kestot] :
         {std::pair{"tasainen", tasainen}, std::pair{"nykivä", nykiva},
          std::pair{"hidas", hidas}}) {
        Tila t = aja(kestot);
        std::println("{:9} askelia {:2}, y = {:.6f} m", nimi, t.askelia,
                     t.y);
    }
}
