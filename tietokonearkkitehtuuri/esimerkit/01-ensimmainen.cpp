// Ensimmäinen ajo: kootaan ohjelma, ajetaan se käskytason
// simulaattorilla ja lasketaan, millaisia käskyjä suoritettiin.
#include <map>
#include <print>
#include <string>

#include "yhteinen/kone.hpp"
#include "yhteinen/ohjelmat.hpp"

int main() {
    // @alku ajo
    const rv::Ohjelma ohjelma = rv::koota(ohjelmat::summa);
    rv::Kone kone(ohjelma);
    const std::vector<rv::Tapahtuma> jalki = kone.aja();
    std::println("tuloste: {}", kone.tuloste);
    std::println("koodia: {} tavua ({} käskyä)",
                 ohjelma.nimiot.at("taulukko"),
                 ohjelma.nimiot.at("taulukko") / 4);
    std::println("suoritettuja käskyjä: {}", jalki.size());
    // @loppu ajo
    // @alku jakauma
    std::map<std::string, int> luokat;
    for (const rv::Tapahtuma& t : jalki) {
        const char* luokka = t.lataus     ? "lataus"
                             : t.talletus ? "talletus"
                             : t.haara    ? "haara"
                             : t.hyppy    ? "hyppy"
                                          : "laskenta";
        ++luokat[luokka];
    }
    for (const auto& [luokka, n] : luokat)
        std::println("{:<9} {:5} {:5.1f} %", luokka, n,
                     100.0 * n / static_cast<double>(jalki.size()));
    // @loppu jakauma
}
