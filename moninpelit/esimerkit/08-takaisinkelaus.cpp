// Viiveen kompensointi: ampuja tähtää kohteeseen, jonka hän näkee
// menneisyydessä (oma viive + interpolointipuskuri). Palvelin kelaa
// kohteiden sijainnit ampujan näkemään hetkeen ennen osumantarkistusta.
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <print>

#include "yhteinen/verkko.hpp"

constexpr std::int64_t PUSKURI = 100;   // ampujan interpolointiviive
constexpr std::int64_t LEVEYS = 400;    // osuma-alueen leveys (mm)
constexpr std::int64_t SUOJA = 1000;    // x >= SUOJA: kohde seinän takana
constexpr std::int64_t KELAUS_MAX = 400;  // pidempää ei korvata

// Kohde juoksee edestakaisin seinän taakse ja takaisin, 2 m/s.
std::int64_t kohde_x(std::int64_t t) {
    const std::int64_t v = (t * 2) % 2400;
    return v < 1200 ? v : 2400 - v;
}

// @alku historia
// Palvelin tallentaa jokaisen tikin sijainnit noin sekunnin ajalta.
struct Historia {
    std::deque<std::pair<std::int64_t, std::int64_t>> tikit;  // aika, x

    void tallenna(std::int64_t aika, std::int64_t x) {
        tikit.emplace_back(aika, x);
        while (tikit.size() > 50) {
            tikit.pop_front();
        }
    }
    // Sijainti annetulla hetkellä (lähin tallennettu tikki).
    std::int64_t kelaa(std::int64_t hetki) const {
        std::int64_t x = tikit.front().second;
        for (const auto& [aika, paikka] : tikit) {
            if (aika <= hetki) {
                x = paikka;
            }
        }
        return x;
    }
};
// @loppu historia

int main(int argc, char**) {
    loki_paalla = argc > 1;
    std::println("{:>6} {:>14} {:>12} {:>15}", "viive", "ilman kelausta",
                 "kelauksella", "seinän takana");
    for (std::int64_t viive : {30, 60, 150, 250}) {
        Historia historia;
        Pcg32 satunnainen(3);
        int ilman = 0, kelattu = 0, takana = 0, laukauksia = 0;
        for (std::int64_t t = 0; t < 60'000; t += 20) {  // 50 tikkiä/s
            historia.tallenna(t, kohde_x(t));
            if (viive == 150 && t < 4000) {
                loki("X {} {}", t, kohde_x(t));  // kuvitusta varten
            }
            if (t < 1000 || satunnainen.valilta(10) != 0) {
                continue;
            }
            // @alku laukaus
            // Ampuja näkee kohteen hetkellä nyt - viive - puskuri ja
            // tähtää täsmälleen siihen. Laukaus saapuu palvelimelle
            // 'viive' myöhemmin; palvelimen aika on silloin t.
            const std::int64_t nakyi = t - 2 * viive - PUSKURI;
            const std::int64_t tahtays = kohde_x(nakyi);
            if (tahtays >= SUOJA) {
                continue;  // ampuja ei näe seinän taakse
            }
            ++laukauksia;
            if (std::abs(tahtays - kohde_x(t)) <= LEVEYS / 2) {
                ++ilman;
            }
            // Kelaus: ampuja kertoo näkemänsä hetken; liian vanhaa ei
            // hyväksytä, ettei suuri viive tai huijari saa etua.
            const std::int64_t hetki = std::max(nakyi, t - KELAUS_MAX);
            if (std::abs(tahtays - historia.kelaa(hetki)) <= LEVEYS / 2) {
                ++kelattu;
                takana += kohde_x(t) >= SUOJA;  // kohde jo turvassa
            }
            // @loppu laukaus
            if (viive == 150 && t < 8000) {
                loki("L {} {} {} {} {} {}", t, nakyi, tahtays, hetki,
                     historia.kelaa(hetki), kohde_x(t));
            }
        }
        std::println("{:>3} ms {:>13} % {:>11} % {:>14} %", viive,
                     ilman * 100 / laukauksia, kelattu * 100 / laukauksia,
                     takana * 100 / laukauksia);
    }
}
