#include "piirto.hpp"

#include <array>
#include <cmath>
#include <fstream>

namespace {

constexpr std::uint32_t TAUSTA = 0x101830, PELAAJA = 0x40c0ff,
                        KIDE = 0xffe040, MIINA = 0xe04040,
                        TEKSTI = 0xe0e0e0;

void suorakulmio(Kuvapuskuri& k, int x, int y, int w, int h,
                 std::uint32_t vari) {
    for (int j = std::max(y, 0); j < std::min(y + h, Kuvapuskuri::H); ++j) {
        for (int i = std::max(x, 0); i < std::min(x + w, Kuvapuskuri::W);
             ++i) {
            k.pikselit[static_cast<std::size_t>(j * Kuvapuskuri::W + i)] =
                vari;
        }
    }
}

void ympyra(Kuvapuskuri& k, const Kappale& p, std::uint32_t vari) {
    const int cx = static_cast<int>(std::lround(p.x));
    const int cy = static_cast<int>(std::lround(p.y));
    const int r = static_cast<int>(p.sade);
    for (int j = -r; j <= r; ++j) {
        for (int i = -r; i <= r; ++i) {
            if (i * i + j * j <= r * r) {
                suorakulmio(k, cx + i, cy + j, 1, 1, vari);
            }
        }
    }
}

// 3x5 pikselin numerot: jokainen rivi kolme bittiä.
constexpr std::array<std::array<int, 5>, 10> NUMEROT{{
    {7, 5, 5, 5, 7}, {2, 6, 2, 2, 7}, {7, 1, 7, 4, 7}, {7, 1, 7, 1, 7},
    {5, 5, 7, 1, 1}, {7, 4, 7, 1, 7}, {7, 4, 7, 5, 7}, {7, 1, 1, 1, 1},
    {7, 5, 7, 5, 7}, {7, 5, 7, 1, 7},
}};

void luku(Kuvapuskuri& k, int arvo, int x, int y) {
    const std::string s = std::to_string(arvo);
    for (char c : s) {
        const auto& kuvio = NUMEROT[static_cast<std::size_t>(c - '0')];
        for (int j = 0; j < 5; ++j) {
            for (int i = 0; i < 3; ++i) {
                if (kuvio[static_cast<std::size_t>(j)] & (4 >> i)) {
                    suorakulmio(k, x + i, y + j, 1, 1, TEKSTI);
                }
            }
        }
        x += 4;
    }
}

}  // namespace

// @alku piirra
void piirra(const Peli& peli, Kuvapuskuri& kuva) {
    suorakulmio(kuva, 0, 0, Kuvapuskuri::W, Kuvapuskuri::H, TAUSTA);
    for (const Kappale& k : peli.kiteet) {
        ympyra(kuva, k, KIDE);
    }
    for (const Kappale& m : peli.miinat) {
        ympyra(kuva, m, MIINA);
    }
    // Suojattu pelaaja vilkkuu: piirretään joka toisella 0,1 s:n jaksolla.
    const bool nakyy = peli.suoja == 0.0 || (peli.ruutu / 6) % 2 == 0;
    if (nakyy && !peli.ohi) {
        ympyra(kuva, peli.pelaaja, PELAAJA);
    }
    luku(kuva, peli.pisteet, 2, 2);
    for (int i = 0; i < peli.elamat; ++i) {
        suorakulmio(kuva, Kuvapuskuri::W - 6 - 5 * i, 2, 3, 5, PELAAJA);
    }
}
// @loppu piirra

std::uint32_t Kuvapuskuri::tarkistussumma() const {
    std::uint32_t h = 2166136261u;
    for (std::uint32_t p : pikselit) {
        for (int i = 0; i < 3; ++i) {
            h = (h ^ ((p >> (8 * i)) & 0xffu)) * 16777619u;
        }
    }
    return h;
}

void Kuvapuskuri::tallenna_ppm(const std::string& polku) const {
    std::ofstream f(polku, std::ios::binary);
    f << "P6\n" << W << ' ' << H << "\n255\n";
    for (std::uint32_t p : pikselit) {
        f.put(static_cast<char>(p >> 16)).put(static_cast<char>(p >> 8))
            .put(static_cast<char>(p));
    }
}
