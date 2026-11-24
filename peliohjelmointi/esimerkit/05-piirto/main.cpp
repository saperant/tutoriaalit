// Pieni 2D-näkymä: ruutukartta, kolikot ja animoitu hahmo, jota kamera
// seuraa. Ruutu tallennetaan PPM-kuvaksi ja tulostetaan merkkeinä.
#include "atlas.hpp"
#include "kamera.hpp"
#include "kuva.hpp"

#include <array>
#include <print>
#include <string_view>

constexpr int RUUTU = 8;  // ruutukartan ruudun koko pikseleinä

constexpr std::array<std::pair<char, Vari>, 5> PALETTI{{
    {'#', {120, 72, 40, 255}},   // tiili
    {'k', {240, 200, 40, 255}},  // kulta
    {'h', {60, 120, 220, 255}},  // hahmo
    {'s', {250, 220, 180, 255}}, // iho
    {'m', {20, 20, 20, 255}},    // musta
}};

// @alku atlas
// Atlas: kaikki spritet samassa kuvassa vierekkäin, 8x8 pikseliä kukin.
constexpr std::array<std::string_view, 8> ATLAS = {
    "########...kk.....ss......ss....",
    "#..#..#...kkkk...hhhh....hhhh...",
    "########.kk..kk..hmhh....hmhh...",
    "..#..#...kk..kk..hhhh....hhhh...",
    "########.kk..kk...hh......hh....",
    "#..#..#...kkkk...hhhh....hhhh...",
    "########...kk....h..h.....hh....",
    "..#..#...........h..h.....h.h...",
};
constexpr Alue TIILI{0, 0, 8, 8}, KOLIKKO{8, 0, 8, 8};
const Animaatio KAVELY{{{16, 0, 8, 8}, {24, 0, 8, 8}}, 0.15, true};
// @loppu atlas

constexpr std::array<std::string_view, 4> KARTTA = {
    "                    o       o      ",
    "        o     ###      ###         ",
    "     ####                    ##    ",
    "###################################",
};

int main() {
    const Kuva atlas = ascii_kuvaksi(ATLAS, PALETTI);
    const double maailman_leveys = KARTTA[0].size() * RUUTU;
    Kamera kamera{0.0, 0.0, 64, 32};
    double pelaaja_x = 10.0;
    double aika = 0.0;
    constexpr double dt = 1.0 / 60.0;
    for (int ruutu = 0; ruutu < 180; ++ruutu) {  // 3 sekuntia
        pelaaja_x += 50.0 * dt;
        aika += dt;
        kamera.seuraa(pelaaja_x, maailman_leveys);
    }

    // @alku piirto
    Kuva ruutu(kamera.leveys, kamera.korkeus, Vari{30, 30, 60, 255});
    int piirretty = 0;
    // Piirretään vain näkyvät ruudut (karsinta).
    const int eka = static_cast<int>(kamera.x) / RUUTU;
    const int vika = (static_cast<int>(kamera.x) + kamera.leveys) / RUUTU;
    for (int ry = 0; ry < static_cast<int>(KARTTA.size()); ++ry) {
        for (int rx = eka; rx <= vika; ++rx) {
            const char c = KARTTA[ry][static_cast<std::size_t>(rx)];
            if (c == ' ') {
                continue;
            }
            const Alue lahde = (c == '#') ? TIILI : KOLIKKO;
            piirra(ruutu, atlas, lahde, kamera.ruudulle_x(rx * RUUTU),
                   kamera.ruudulle_y(ry * RUUTU));
            ++piirretty;
        }
    }
    piirra(ruutu, atlas, KAVELY.kuva(aika), kamera.ruudulle_x(pelaaja_x),
           kamera.ruudulle_y(2.0 * RUUTU));
    // @loppu piirto

    ruutu.tallenna_ppm("ruutu.ppm");
    std::println("pelaaja x = {:.1f}, kamera x = {:.1f}", pelaaja_x,
                 kamera.x);
    std::println("piirrettyjä ruutuja {}, kartassa {}", piirretty,
                 KARTTA.size() * KARTTA[0].size());
    std::println("tarkistussumma {:08x}", ruutu.tarkistussumma());
    // Ruutu merkkeinä: jokainen toinen pikselirivi.
    for (int y = 0; y < ruutu.korkeus(); y += 2) {
        for (int x = 0; x < ruutu.leveys(); ++x) {
            char merkki = ' ';
            for (const auto& [m, v] : PALETTI) {
                if (ruutu(x, y) == v) {
                    merkki = m;
                }
            }
            std::print("{}", merkki);
        }
        std::println();
    }
}
