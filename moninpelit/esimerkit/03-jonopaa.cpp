// Miksi peli ei käytä TCP:tä tilan lähettämiseen: kadonnut paketti
// pysäyttää kaikki sen jälkeen tulleet, kunnes uudelleenlähetys saapuu
// (head-of-line blocking). UDP:llä uusin saapunut tila otetaan heti
// käyttöön ja kadonnut korvautuu seuraavalla.
#include <algorithm>
#include <array>
#include <cstdint>
#include <print>
#include <vector>

#include "yhteinen/verkko.hpp"

constexpr int VALI = 50;        // tila 20 kertaa sekunnissa
constexpr int VIIVE = 50;       // yhden suunnan viive
constexpr int VARINA = 20;
constexpr int RTO = 250;        // uudelleenlähetyksen odotus
constexpr int HAVIO = 20;       // promillea
constexpr int PAKETIT = 2000;

int main(int argc, char**) {
    loki_paalla = argc > 1;
    Pcg32 satunnainen(11);
    std::vector<std::int64_t> udp(PAKETIT, -1), tcp(PAKETIT);
    // @alku saapuminen
    for (int k = 0; k < PAKETIT; ++k) {
        const std::int64_t lahetys = std::int64_t{k} * VALI;
        std::int64_t yritys = lahetys;
        for (bool ensimmainen = true;; ensimmainen = false) {
            const bool katosi = satunnainen.valilta(1000) < HAVIO;
            const std::int64_t perilla =
                yritys + VIIVE + satunnainen.valilta(VARINA + 1);
            if (!katosi) {
                if (ensimmainen) {
                    udp[k] = perilla;  // UDP ei lähetä uudelleen
                }
                tcp[k] = perilla;
                break;
            }
            yritys += RTO;  // TCP lähettää saman tavun uudelleen
        }
    }
    // TCP luovuttaa tavut sovellukselle järjestyksessä: paketti k on
    // käytettävissä vasta, kun kaikki aiemmat ovat perillä.
    for (int k = 1; k < PAKETIT; ++k) {
        tcp[k] = std::max(tcp[k], tcp[k - 1]);
    }
    // @loppu saapuminen
    for (int k = 0; k < PAKETIT; ++k) {
        loki("{} {} {}", k, udp[k], tcp[k]);
    }

    // @alku ika
    // Näytetyn tilan ikä joka millisekunti: kauanko sitten uusin
    // käytettävissä oleva tila lähetettiin.
    auto mittaa = [](const std::vector<std::int64_t>& saapuu) {
        std::int64_t summa = 0, suurin = 0, jumissa = 0;
        int uusin = -1;
        const std::int64_t loppu = std::int64_t{PAKETIT} * VALI;
        for (std::int64_t t = 1000; t < loppu; ++t) {
            for (int k = uusin + 1; k < PAKETIT; ++k) {
                if (saapuu[k] >= 0 && saapuu[k] <= t) {
                    uusin = k;  // UDP: vanhempia ei odoteta
                }
            }
            const std::int64_t ika = t - std::int64_t{uusin} * VALI;
            summa += ika;
            suurin = std::max(suurin, ika);
            jumissa += ika > 200;
        }
        return std::array{summa / (loppu - 1000), suurin, jumissa};
    };
    // @loppu ika
    for (auto [nimi, saapuu] : {std::pair{"UDP", &udp}, {"TCP", &tcp}}) {
        const auto [ka, suurin, jumissa] = mittaa(*saapuu);
        std::println("{}: tilan ikä ka. {} ms, suurin {} ms, "
                     "yli 200 ms {} ms ajasta",
                     nimi, ka, suurin, jumissa);
    }
}
