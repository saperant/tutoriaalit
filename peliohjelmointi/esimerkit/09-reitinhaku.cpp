// Reitinhaku ruudukossa: Dijkstran algoritmi ja A* löytävät yhtä
// halvan reitin, mutta A* tutkii alle puolet ruuduista.
#include "yhteinen/reitinhaku.hpp"

#include <array>
#include <cstring>
#include <print>
#include <string>

constexpr std::array<std::string_view, 11> RIVIT = {
    "##########################",
    "#............#...........#",
    "#............#...........#",
    "#..A.........#.......B...#",
    "#............#...........#",
    "#.......#....#...........#",
    "#.......#....~...........#",
    "#.......#....~...........#",
    "#.......#....#...........#",
    "#.......#................#",
    "##########################",
};

Ruutu etsi(char merkki) {
    for (int y = 0; y < static_cast<int>(RIVIT.size()); ++y) {
        const auto x = RIVIT[static_cast<std::size_t>(y)].find(merkki);
        if (x != std::string_view::npos) {
            return {static_cast<int>(x), y};
        }
    }
    return {-1, -1};
}

int main(int argc, char** argv) {
    const Kartta kartta{RIVIT};
    const Ruutu alku = etsi('A'), maali = etsi('B');

    // Käyrätila kuvitusta varten: ruutujen käsittelyjärjestys.
    if (argc > 1 && std::strcmp(argv[1], "k") == 0) {
        for (const auto rivi : RIVIT) {
            std::println("kartta {}", rivi);
        }
        for (auto [nimi, h] : {std::pair{"dijkstra", &nolla},
                               std::pair{"astar", &manhattan}}) {
            const Reitti r = hae_reitti(kartta, alku, maali, h);
            for (std::size_t n = 0; n < r.tutkitut.size(); ++n) {
                std::println("{} tutkittu {} {} {}", nimi, n,
                             r.tutkitut[n].x, r.tutkitut[n].y);
            }
            for (const Ruutu p : r.polku) {
                std::println("{} polku {} {}", nimi, p.x, p.y);
            }
        }
        return 0;
    }

    // @alku vertailu
    const Reitti d = hae_reitti(kartta, alku, maali, nolla);
    const Reitti a = hae_reitti(kartta, alku, maali, manhattan);
    std::println("Dijkstra:        hinta {}, askelia {}, tutkittu {} ruutua",
                 d.hinta, d.polku.size() - 1, d.tutkitut.size());
    std::println("A* (Manhattan):  hinta {}, askelia {}, tutkittu {} ruutua",
                 a.hinta, a.polku.size() - 1, a.tutkitut.size());
    // @loppu vertailu

    std::array<std::string, RIVIT.size()> kuva;
    for (std::size_t y = 0; y < RIVIT.size(); ++y) {
        kuva[y] = RIVIT[y];
    }
    for (const Ruutu p : a.polku) {
        auto& m = kuva[static_cast<std::size_t>(p.y)]
                      [static_cast<std::size_t>(p.x)];
        if (m == '.' || m == '~') {
            m = '*';
        }
    }
    for (const auto& rivi : kuva) {
        std::println("{}", rivi);
    }

    // Maali, johon ei pääse: haku käy läpi kaiken saavutettavan.
    constexpr std::array<std::string_view, 5> SULJETTU = {
        "#########",
        "#A...#..#",
        "#....#.B#",
        "#....#..#",
        "#########",
    };
    const Reitti ei = hae_reitti(Kartta{SULJETTU}, {1, 1}, {7, 2}, manhattan);
    std::println("suljettu huone: polku {}, tutkittu {} ruutua",
                 ei.polku.empty() ? "puuttuu" : "löytyi",
                 ei.tutkitut.size());
}
