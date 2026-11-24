// Syötteen tallennus ja toisto: komennot kirjoitetaan tiedostoon, ja
// toisto tuottaa täsmälleen saman lopputilan (tarkistussumma).
#include <bit>
#include <cstdint>
#include <fstream>
#include <print>
#include <string>
#include <vector>

// @alku komento
enum class Komento : char {
    Vasen = 'V', Oikea = 'O', Hyppy = 'H', Ei = '-'
};

struct Pelaaja {
    double x = 0.0, y = 0.0, vy = 0.0;

    void suorita(Komento k, double dt) {
        switch (k) {
        case Komento::Vasen: x -= 4.0 * dt; break;
        case Komento::Oikea: x += 4.0 * dt; break;
        case Komento::Hyppy:
            if (y == 0.0) {
                vy = 6.0;
            }
            break;
        case Komento::Ei: break;
        }
        vy -= 20.0 * dt;
        y += vy * dt;
        if (y < 0.0) {
            y = 0.0;
            vy = 0.0;
        }
    }
};
// @loppu komento

// @alku tarkistussumma
// FNV-1a tilan biteistä: sama tila tuottaa saman summan.
std::uint64_t tarkistussumma(const Pelaaja& p) {
    std::uint64_t h = 1469598103934665603ULL;
    for (double arvo : {p.x, p.y, p.vy}) {
        auto bitit = std::bit_cast<std::uint64_t>(arvo);
        for (int i = 0; i < 8; ++i) {
            h ^= (bitit >> (8 * i)) & 0xffu;
            h *= 1099511628211ULL;
        }
    }
    return h;
}
// @loppu tarkistussumma

int main() {
    constexpr double dt = 1.0 / 60.0;
    // "Pelaaja pelaa": komennot syntyvät pelin aikana ja tallentuvat.
    const std::string pelattu =
        "OOOOOOOOOOH-------OOOOOVVVVH----------------OOOOO-----";
    Pelaaja alkuperainen;
    {
        std::ofstream tallenne("tallenne.txt");
        for (char c : pelattu) {
            alkuperainen.suorita(static_cast<Komento>(c), dt);
            tallenne << c;
        }
    }
    // @alku toisto
    std::string luettu;
    std::ifstream("tallenne.txt") >> luettu;
    Pelaaja toistettu;
    for (char c : luettu) {
        toistettu.suorita(static_cast<Komento>(c), dt);
    }
    // @loppu toisto
    std::println("ruutuja {}, x = {:.3f}, y = {:.3f}", luettu.size(),
                 toistettu.x, toistettu.y);
    std::println("alkuperäinen {:016x}", tarkistussumma(alkuperainen));
    std::println("toistettu    {:016x}", tarkistussumma(toistettu));
}
