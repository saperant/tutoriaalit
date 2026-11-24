// Ensimmäinen verkkoesimerkki: asiakas lähettää palvelimelle 20
// ping-viestiä, palvelin palauttaa ne heti. Simuloitu yhteys tekee
// tuloksesta saman joka ajolla.
#include <cstdint>
#include <format>
#include <print>
#include <string>

#include "yhteinen/verkko.hpp"

struct Ping {
    int numero;
    std::int64_t lahetetty;
};

int main() {
    // @alku ping
    const Linkki linkki{.viive_ms = 30, .varina_ms = 12,
                        .havio_promille = 50};
    Kanava<Ping> ylos(linkki, 1), alas(linkki, 2);
    int saatu = 0;
    std::string rivi;
    for (std::int64_t nyt = 0; nyt <= 2'500; ++nyt) {  // 1 ms askel
        if (nyt % 100 == 0 && nyt < 2'000) {
            ylos.laheta(nyt, {static_cast<int>(nyt / 100), nyt});
        }
        for (const Ping& p : ylos.vastaanota(nyt)) {
            alas.laheta(nyt, p);  // palvelin vastaa heti
        }
        for (const Ping& p : alas.vastaanota(nyt)) {
            ++saatu;
            rivi += std::format("{}{}:{}", rivi.empty() ? "" : " ",
                                p.numero, nyt - p.lahetetty);
        }
    }
    std::println("ping:kiertoviive ms: {}", rivi);
    std::println("vastauksia {}/20", saatu);
    // @loppu ping
}
