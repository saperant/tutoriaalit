// Käskyjen järjestyksen vaikutus: sama summaussilmukka kolmena
// versiona. Kääntäjä tekee juuri tällaisia muunnoksia.
#include <array>
#include <print>
#include <string>
#include <string_view>

#include "yhteinen/kone.hpp"
#include "yhteinen/liukuhihna.hpp"
#include "yhteinen/ohjelmat.hpp"

// @alku versiot
// Vaihdetaan summa-ohjelman silmukan runko toiseen.
std::string vaihda(std::string_view runko) {
    std::string s(ohjelmat::summa);
    const std::string vanha = R"(summaa: slli t2, t0, 2
        add  t2, s0, t2
        lw   t1, 0(t2)
        add  a0, a0, t1          # käyttää heti ladattua arvoa
        addi t0, t0, 1
        blt  t0, s1, summaa)";
    s.replace(s.find(vanha), vanha.size(), runko);
    return s;
}

// Lataus siirretään kauemmas käytöstä.
constexpr std::string_view jarjestetty = R"(summaa: slli t2, t0, 2
        add  t2, s0, t2
        lw   t1, 0(t2)
        addi t0, t0, 1
        add  a0, a0, t1
        blt  t0, s1, summaa)";

// Indeksin sijaan kasvatetaan osoitinta; loppuehto osoitteena.
constexpr std::string_view osoitin = R"(        mv   t2, s0
        slli t3, s1, 2
        add  t3, s0, t3          # taulukon loppu
summaa: lw   t1, 0(t2)
        addi t2, t2, 4
        add  a0, a0, t1
        blt  t2, t3, summaa)";
// @loppu versiot

int main() {
    // @alku vertailu
    const std::array<std::pair<std::string_view, std::string>, 3> versiot{{
        {"alkuperäinen", std::string(ohjelmat::summa)},
        {"järjestetty", vaihda(jarjestetty)},
        {"osoitin", vaihda(osoitin)}}};
    std::println("{:<13} {:>6} {:>6} {:>5} {:>5} {:>5}  tulos", "versio",
                 "käskyt", "jaksot", "data", "ohj", "CPI");
    for (const auto& [nimi, lahde] : versiot) {
        rv::Kone kone(rv::koota(lahde));
        const auto jalki = kone.aja();
        rv::Laskuri e(2, 64);
        const rv::Tulos t = rv::simuloi(jalki, {.ennustin = &e});
        std::println("{:<13} {:>6} {:>6} {:>5} {:>5} {:>5.2f}  {}", nimi,
                     t.kaskyt, t.syklit, t.datapysahdykset,
                     t.ohjauspysahdykset, t.cpi(), kone.tuloste);
    }
    // @loppu vertailu
}
