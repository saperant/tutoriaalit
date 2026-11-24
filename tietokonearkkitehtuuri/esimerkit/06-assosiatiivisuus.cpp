// Assosiatiivisuus, korvauspolitiikka ja hutien 3C-luokittelu.
#include <algorithm>
#include <array>
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/ohjelmat.hpp"
#include "yhteinen/valimuisti.hpp"

// Ohjelman datamuistiviitteiden osoitteet suoritusjärjestyksessä.
std::vector<rv::u32> osoitteet(std::string_view lahde) {
    rv::Kone kone(rv::koota(lahde));
    std::vector<rv::u32> v;
    for (const rv::Tapahtuma& t : kone.aja())
        if (t.lataus || t.talletus) v.push_back(t.osoite);
    return v;
}

int main() {
    const std::vector<rv::u32> jalki = osoitteet(ohjelmat::matriisi);
    // @alku tiet
    std::println("matriisi, 16 B lohkot; osumasuhde (%)");
    std::println("{:<6} {:<12} {:>9} {:>9} {:>9}", "tiet", "korvaus",
                 "256 B", "512 B", "1024 B");
    const std::array<std::pair<rv::Korvaus, std::string_view>, 3>
        politiikat{{{rv::Korvaus::LRU, "LRU"}, {rv::Korvaus::FIFO, "FIFO"},
                    {rv::Korvaus::Satunnainen, "satunnainen"}}};
    for (const rv::u32 tiet : {1u, 2u, 4u, 64u}) {
        for (const auto& [korvaus, nimi] : politiikat) {
            if (tiet == 1 && korvaus != rv::Korvaus::LRU) continue;
            std::print("{:<6} {:<12}", tiet == 64 ? "täysi" :
                       std::to_string(tiet), tiet == 1 ? "-" : nimi);
            for (const rv::u32 koko : {256u, 512u, 1024u}) {
                rv::Valimuisti v({.koko = koko, .lohko = 16,
                                  .tiet = std::min(tiet, koko / 16),
                                  .korvaus = korvaus});
                for (const rv::u32 o : jalki) v.viittaa(o, false);
                std::print(" {:>9.1f}", 100 * v.tilastot().osumasuhde());
            }
            std::println();
        }
    }
    // @loppu tiet
    // @alku kolme_c
    std::println("\n3C, matriisi: pakolliset / kapasiteetti / ristiriita");
    for (const rv::u32 koko : {256u, 512u, 1024u, 2048u}) {
        for (const rv::u32 tiet : {1u, 2u, 4u}) {
            const rv::KolmeC c = rv::luokittele(
                jalki, {.koko = koko, .lohko = 16, .tiet = tiet});
            std::println("{:>5} B {}-tie: {:4} {:6} {:6}", koko, tiet,
                         c.pakolliset, c.kapasiteetti, c.ristiriita);
        }
    }
    // @loppu kolme_c
}
