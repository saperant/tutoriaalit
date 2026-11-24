// Verkon todellisuus mitattuna: 1000 pakettia 20 ms välein simuloidun
// yhteyden yli. Lasketaan viive, värinä, häviö ja järjestyksen
// muutokset.
#include <algorithm>
#include <cstdint>
#include <print>

#include "yhteinen/verkko.hpp"

struct Paketti {
    int numero;
    std::int64_t lahetetty;
};

void mittaa(const char* nimi, Linkki linkki) {
    Kanava<Paketti> kanava(linkki, 7);
    int saapui = 0, epajarjestyksessa = 0, suurin_numero = -1;
    std::int64_t summa = 0, pienin = 1'000'000, suurin = 0;
    for (std::int64_t t = 0; t < 21'000; ++t) {  // 1 ms:n askel
        if (t % 20 == 0 && t / 20 < 1000) {
            kanava.laheta(t, {static_cast<int>(t / 20), t});
        }
        for (const Paketti& p : kanava.vastaanota(t)) {
            const std::int64_t v = t - p.lahetetty;
            ++saapui;
            summa += v;
            pienin = std::min(pienin, v);
            suurin = std::max(suurin, v);
            if (p.numero < suurin_numero) {
                ++epajarjestyksessa;
            }
            suurin_numero = std::max(suurin_numero, p.numero);
        }
    }
    std::println("{:<8} saapui {:>4}, hukka {:>2}, järjestys vaihtui {:>3}, "
                 "viive {}–{} ms (ka. {})",
                 nimi, saapui, kanava.hukattu(), epajarjestyksessa, pienin,
                 suurin, summa / saapui);
}

int main() {
    // @alku linkit
    mittaa("kuitu", {.viive_ms = 8, .varina_ms = 1});
    mittaa("kaapeli", {.viive_ms = 25, .varina_ms = 10,
                       .havio_promille = 5});
    mittaa("mobiili", {.viive_ms = 45, .varina_ms = 60,
                       .havio_promille = 20});
    // @loppu linkit
}
