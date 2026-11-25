// Taitoluokitus ja otteluiden muodostus: Elo-luvut lähestyvät pelaajien
// todellista taitoa, ja luokituksen mukaan muodostetut ottelut ovat
// tasaisempia kuin satunnaiset.
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <numeric>
#include <print>
#include <vector>

#include "yhteinen/verkko.hpp"

// @alku elo
// Odotettu tulos pelaajalle a (0..1) luokitusten erotuksesta.
double odotus(double a, double b) {
    return 1.0 / (1.0 + std::pow(10.0, (b - a) / 400.0));
}
// Voitto 1, tappio 0. K määrää, kuinka paljon yksi ottelu siirtää.
void paivita(double& a, double& b, double tulos_a, double k = 32) {
    const double e = odotus(a, b);
    a += k * (tulos_a - e);
    b -= k * (tulos_a - e);
}
// @loppu elo

constexpr int N = 200;

int main(int argc, char**) {
    const bool kayra = argc > 1;  // käyrätila: tulostaa joka kierroksen
    Pcg32 r(12);
    std::vector<double> taito(N), luku(N, 1500);
    for (double& t : taito) {
        t = 1000 + r.valilta(1001);  // todellinen, piilossa oleva taito
    }
    std::println("{:<11} {:>8} {:>18} {:>14}", "ottel./pel.", "virhe",
                 "tasaisia, luokitus", "satunnainen");
    int otteluita = 0;
    for (int kierros = 1; kierros <= 200; ++kierros) {
        // @alku jono
        // Jono järjestetään luokituksen mukaan ja vierekkäiset
        // pelaavat; satunnaisesta jonosta vertailun vuoksi.
        std::vector<int> jono(N), satunnainen(N);
        std::iota(jono.begin(), jono.end(), 0);
        std::iota(satunnainen.begin(), satunnainen.end(), 0);
        std::stable_sort(jono.begin(), jono.end(), [&](int a, int b) {
            return luku[a] < luku[b];
        });
        // @loppu jono
        for (int i = N - 1; i > 0; --i) {  // Fisher–Yates
            std::swap(satunnainen[i], satunnainen[r.valilta(i + 1)]);
        }
        int tasaiset = 0, tasaiset_satunnaisesti = 0;
        for (int i = 0; i + 1 < N; i += 2) {
            const int a = jono[i], b = jono[i + 1];
            tasaiset += std::abs(taito[a] - taito[b]) < 100;
            tasaiset_satunnaisesti +=
                std::abs(taito[satunnainen[i]] -
                         taito[satunnainen[i + 1]]) < 100;
            const bool voitto = r.valilta(1'000'000) <
                                odotus(taito[a], taito[b]) * 1'000'000;
            paivita(luku[a], luku[b], voitto ? 1.0 : 0.0);
        }
        ++otteluita;
        if (kayra || kierros == 1 || kierros == 10 || kierros == 50 ||
            kierros == 200) {
            // Luokitus ja taito ovat eri asteikolla: verrataan keskiarvoon.
            const double ka_l = std::accumulate(luku.begin(), luku.end(),
                                                0.0) / N;
            const double ka_t = std::accumulate(taito.begin(), taito.end(),
                                                0.0) / N;
            double virhe = 0;
            for (int i = 0; i < N; ++i) {
                virhe += std::abs((luku[i] - ka_l) - (taito[i] - ka_t));
            }
            std::println("{:<11} {:>8.0f} {:>16} % {:>12} %", otteluita,
                         virhe / N, tasaiset * 100 / (N / 2),
                         tasaiset_satunnaisesti * 100 / (N / 2));
        }
    }
}
