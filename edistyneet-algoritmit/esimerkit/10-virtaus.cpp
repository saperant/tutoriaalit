// Maksimivirtaus ja minimileikkaus: kaksi algoritmia, vertailu
// raakaan leikkausten läpikäyntiin ja esimerkkiverkko.
#include <array>
#include <print>
#include <string_view>
#include <vector>

#include "testaus.hpp"
#include "virtaus.hpp"

struct Kaari {
    int u, v;
    long c;
};

// @alku raaka
// Malli: pienin leikkaus käymällä läpi kaikki solmujoukot S, joissa on
// s mutta ei t. Max-flow min-cut -lauseen mukaan se on suurin virta.
static long pienin_leikkaus(int n, const std::vector<Kaari>& kaaret,
                            int s, int t)
{
    long paras = -1;
    for (unsigned maski = 0; maski < (1u << n); ++maski) {
        bool s_mukana = (maski >> s) & 1, t_mukana = (maski >> t) & 1;
        if (!s_mukana || t_mukana) {
            continue;
        }
        long leikkaus = 0;
        for (auto [u, v, c] : kaaret) {
            if (((maski >> u) & 1) && !((maski >> v) & 1)) {
                leikkaus += c;
            }
        }
        if (paras < 0 || leikkaus < paras) {
            paras = leikkaus;
        }
    }
    return paras;
}
// @loppu raaka

int main()
{
    // @alku testi
    for (std::uint64_t siemen = 1; siemen <= 300; ++siemen) {
        Satunnainen s{siemen};
        int n = s.valilta(2, 9);
        std::vector<Kaari> kaaret;
        Virtausverkko verkko{n};
        for (int i = s.valilta(0, 3 * n); i > 0; --i) {
            Kaari k{s.valilta(0, n - 1), s.valilta(0, n - 1),
                    s.valilta(1, 9)};
            kaaret.push_back(k);
            verkko.lisaa_kaari(k.u, k.v, k.c);
        }
        long odotettu = pienin_leikkaus(n, kaaret, 0, n - 1);
        vaadi(verkko.edmonds_karp(0, n - 1) == odotettu, "Edmonds-Karp");
        verkko.nollaa();
        vaadi(verkko.dinic(0, n - 1) == odotettu, "Dinic");
    }
    std::println("vertailutesti: 300 verkkoa, molemmat algoritmit "
                 "= pienin leikkaus");
    // @loppu testi

    // @alku esimerkki
    // Varmuuskopiot siirretään konesalista A konesaliin F. Kapasiteetit
    // ovat Gbit/s. Kuinka paljon yhteydet riittävät siirtämään, ja mikä
    // on pullonkaula?
    constexpr std::array<std::string_view, 6> nimi{"A", "B", "C", "D", "E",
                                                    "F"};
    const std::vector<Kaari> yhteydet{
        {0, 1, 10}, {0, 2, 10}, {1, 2, 2}, {1, 3, 4}, {1, 4, 8},
        {2, 4, 9}, {4, 3, 6}, {3, 5, 10}, {4, 5, 10}};
    Virtausverkko verkko{6};
    for (auto [u, v, c] : yhteydet) {
        verkko.lisaa_kaari(u, v, c);
    }
    std::println("Edmonds-Karp: {} Gbit/s, {} lisäyspolkua",
                 verkko.edmonds_karp(0, 5), verkko.polkuja);
    verkko.nollaa();
    std::println("Dinic:        {} Gbit/s, {} vaihetta", verkko.dinic(0, 5),
                 verkko.vaiheita);
    auto puoli = verkko.s_puoli(0);
    std::print("minimileikkaus:");
    for (auto [u, v, c] : yhteydet) {
        if (puoli[static_cast<std::size_t>(u)]
            && !puoli[static_cast<std::size_t>(v)]) {
            std::print(" {}-{} ({})", nimi[static_cast<std::size_t>(u)],
                       nimi[static_cast<std::size_t>(v)], c);
        }
    }
    std::println("");
    // @loppu esimerkki

    // Kaarten virrat ja leikkauksen lähdepuoli: kirjan kuva piirretään
    // näistä riveistä (kaaviot/tee.py). Kaaren i tunniste on 2 * i.
    std::print("virrat:");
    for (std::size_t i = 0; i < yhteydet.size(); ++i) {
        auto [u, v, c] = yhteydet[i];
        std::print(" {}-{} {}/{}", nimi[static_cast<std::size_t>(u)],
                   nimi[static_cast<std::size_t>(v)],
                   verkko.virta(static_cast<int>(2 * i)), c);
    }
    std::print("\nlähteen puoli:");
    for (std::size_t v = 0; v < nimi.size(); ++v) {
        if (puoli[v]) {
            std::print(" {}", nimi[v]);
        }
    }
    std::println("");
}
