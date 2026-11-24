// Silmukoiden järjestys: 32 x 32 -matriisin summa riveittäin ja
// sarakkeittain. Sama käskymäärä, aivan eri välimuistikäyttäytyminen.
#include <print>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/valimuisti.hpp"

// @alku ohjelma
// Ulompi silmukka kasvattaa osoitetta askeleella a, sisempi askeleella
// b. Riveittäin: a = 128 (rivi), b = 4 (sana). Sarakkeittain toisin päin.
std::string summaus(int a, int b) {
    return std::format(R"(
        la   s0, M
        li   s1, 32
        li   a0, 0
        li   t0, 0               # ulompi laskuri
ulompi: mv   t2, s0              # sisemmän silmukan osoitin
        li   t1, 0
sisempi:
        lw   t3, 0(t2)
        add  a0, a0, t3
        addi t2, t2, {1}
        addi t1, t1, 1
        blt  t1, s1, sisempi
        addi s0, s0, {0}
        addi t0, t0, 1
        blt  t0, s1, ulompi
        li   a7, 10
        ecall
M:      .zero 4096
)", a, b);
}
// @loppu ohjelma

int main() {
    // @alku vertailu
    std::println("{:<15} {:>7} {:>9} {:>9} {:>9}", "järjestys", "käskyt",
                 "1 KiB/16", "1 KiB/64", "8 KiB/16");
    for (const auto& [nimi, a, b] : {std::tuple{"riveittäin", 128, 4},
                                     {"sarakkeittain", 4, 128}}) {
        rv::Kone kone(rv::koota(summaus(a, b)));
        const std::vector<rv::Tapahtuma> jalki = kone.aja();
        std::print("{:<15} {:>7}", nimi, jalki.size());
        for (const auto& [koko, lohko] : {std::pair{1024u, 16u},
                                          {1024u, 64u}, {8192u, 16u}}) {
            rv::Valimuisti vm({.koko = koko, .lohko = lohko, .tiet = 2});
            for (const rv::Tapahtuma& t : jalki)
                if (t.lataus) vm.viittaa(t.osoite, false);
            std::print(" {:>8.1f}%", 100 * vm.tilastot().osumasuhde());
        }
        std::println();
    }
    // @loppu vertailu
}
