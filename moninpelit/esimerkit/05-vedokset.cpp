// Tilannevedosten kaistankulutus: koko tila joka tikki, kvantisoitu
// tila, delta suhteessa asiakkaan kuittaamaan vedokseen ja lopuksi
// kiinnostusalue. 64 entiteettiä, 30 vedosta sekunnissa.
#include <array>
#include <cstdint>
#include <print>
#include <vector>

#include "yhteinen/verkko.hpp"

constexpr int N = 64;
constexpr int TIKIT = 30;
constexpr int KUITTAUSVIIVE = 4;  // tikkiä: vedos kuitataan ~130 ms:ssa

struct Entiteetti {
    std::int32_t x, y;  // senttimetreinä, 0..102 400
    std::int32_t suunta;  // 0..511
    std::int32_t terveys;
    bool operator==(const Entiteetti&) const = default;
};
using Vedos = std::array<Entiteetti, N>;

// @alku koot
constexpr int NAIIVI_TAVUA = 2 + 4 * 4;          // tunniste ja 4 kenttää
constexpr int PAKATTU_BITTEJA = 17 + 17 + 9 + 7;  // kuten luvussa 5.1

// Delta: entiteetin tunniste ja muutosbitti joka kentälle, sitten vain
// muuttuneet kentät. Muuttumattomia entiteettejä ei lähetetä lainkaan.
int delta_bitteja(const Vedos& pohja, const Vedos& uusi, auto mukaan) {
    int bitteja = 7;  // muuttuneiden entiteettien määrä
    for (int i = 0; i < N; ++i) {
        const Entiteetti& a = pohja[i];
        const Entiteetti& b = uusi[i];
        if (a == b || !mukaan(b)) {
            continue;
        }
        bitteja += 6 + 4;  // tunniste ja neljä muutosbittiä
        bitteja += (a.x != b.x) * 17 + (a.y != b.y) * 17;
        bitteja += (a.suunta != b.suunta) * 9 + (a.terveys != b.terveys) * 7;
    }
    return bitteja;
}
// @loppu koot

int main() {
    Pcg32 satunnainen(5);
    Vedos tila{};
    for (Entiteetti& e : tila) {
        e = {static_cast<std::int32_t>(satunnainen.valilta(102'400)),
             static_cast<std::int32_t>(satunnainen.valilta(102'400)),
             static_cast<std::int32_t>(satunnainen.valilta(512)), 100};
    }
    std::vector<Vedos> historia;
    long naiivi = 0, pakattu = 0, delta = 0, alue = 0;
    const int KIERROKSIA = 600;
    for (int tikki = 0; tikki < KIERROKSIA; ++tikki) {
        // Kolmannes liikkuu, osa kääntyy, harva menettää terveyttä.
        for (int i = 0; i < N; ++i) {
            Entiteetti& e = tila[i];
            if (i % 3 == 0) {
                e.x = (e.x + 40 + 102'400) % 102'400;
                e.suunta = (e.suunta + 3) % 512;
            }
            if (satunnainen.valilta(100) == 0 && e.terveys > 0) {
                e.terveys -= 10;
            }
        }
        historia.push_back(tila);
        // @alku vertailu
        naiivi += N * NAIIVI_TAVUA * 8;
        pakattu += N * PAKATTU_BITTEJA;
        const Vedos pohja = tikki >= KUITTAUSVIIVE
                                ? historia[tikki - KUITTAUSVIIVE]
                                : Vedos{};
        delta += delta_bitteja(pohja, tila, [](const Entiteetti&) {
            return true;
        });
        // Kiinnostusalue: vain 200 metrin säteellä olevat (pelaaja 0).
        const Entiteetti& oma = tila[0];
        alue += delta_bitteja(pohja, tila, [&](const Entiteetti& e) {
            const std::int64_t dx = e.x - oma.x, dy = e.y - oma.y;
            return dx * dx + dy * dy <= std::int64_t{20'000} * 20'000;
        });
        // @loppu vertailu
    }
    for (auto [nimi, bitit] : {std::pair{"koko tila", naiivi},
                               {"kvantisoitu", pakattu},
                               {"delta", delta},
                               {"delta + alue", alue}}) {
        const long tavua = bitit / 8 / KIERROKSIA;
        std::println("{:<13} {:>5} tavua/vedos {:>7.1f} kbit/s", nimi, tavua,
                     static_cast<double>(bitit) / KIERROKSIA * TIKIT / 1000);
    }
}
