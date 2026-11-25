// Kahden asennon välinen interpolointi kolmella tavalla: Eulerin
// kulmat, nlerp ja slerp. Argumenttina annettuun tiedostoon
// piirretään kuvasarja.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku kulma
// Kahden asennon välinen kulma asteina: pienin kierto, joka vie
// toisen toiseksi.
double kulma(Kvat a, Kvat b) {
    return aste(2 * std::acos(std::min(1.0, std::abs(piste(a, b)))));
}
// @loppu kulma

struct Euler {
    double kaanto, nyokkays, kallistus;  // asteina
};
Kvat kvaternioksi(Euler e) {
    return eulerista(rad(e.kaanto), rad(e.nyokkays), rad(e.kallistus));
}

void piirra_kone(Piirtaja& p, const Mat4& m) {
    piirra(p, laatikkoverkko({-0.15, -0.15, -1}, {0.15, 0.15, 1}), m,
           {200, 200, 205});
    piirra(p, laatikkoverkko({-1.2, -0.04, -0.3}, {1.2, 0.04, 0.3}), m,
           {190, 90, 70});
    piirra(p, laatikkoverkko({-0.04, 0.15, 0.6}, {0.04, 0.7, 1}), m,
           {70, 110, 190});
    piirra(p, laatikkoverkko({-0.1, -0.1, -1.3}, {0.1, 0.1, -1}), m,
           {40, 40, 40});
}

int main(int argc, char** argv) {
    // @alku vertailu
    Euler alku{-60, -20, 0}, loppu{80, 50, 90};
    Kvat a = kvaternioksi(alku), b = kvaternioksi(loppu);
    std::println("Asentojen välinen kulma {} astetta", luku(kulma(a, b), 1));
    std::println("    t   Euler: kulma  kierros   nlerp: kulma   "
                 "slerp: kulma");
    for (int i = 0; i <= 4; ++i) {
        double t = i / 4.0;
        Kvat e = kvaternioksi(
            {alku.kaanto + t * (loppu.kaanto - alku.kaanto),
             alku.nyokkays + t * (loppu.nyokkays - alku.nyokkays),
             alku.kallistus + t * (loppu.kallistus - alku.kallistus)});
        // Kierros: kuinka paljon reitti alusta välipisteen kautta
        // loppuun on suoraa reittiä pidempi.
        double kierros = kulma(a, e) + kulma(e, b) - kulma(a, b);
        std::println("{:>5} {:>14} {:>8} {:>14} {:>14}", luku(t),
                     luku(kulma(a, e), 1), luku(kierros, 1),
                     luku(kulma(a, nlerp(a, b, t)), 1),
                     luku(kulma(a, slerp(a, b, t)), 1));
    }
    // @loppu vertailu

    if (argc > 1) {
        Kuva kuva(720, 300, {150, 185, 225});
        Piirtaja p(kuva, perspektiivi(1 / std::tan(rad(16)), 2.4, 0.1, 100) *
                             katse({0, 5, 16}, {0, 0.2, 0}, {0, 1, 0}));
        for (int i = 0; i <= 4; ++i) {
            double t = i / 4.0, x = -6.4 + 3.2 * i;
            Kvat e = kvaternioksi(
                {alku.kaanto + t * (loppu.kaanto - alku.kaanto),
                 alku.nyokkays + t * (loppu.nyokkays - alku.nyokkays),
                 alku.kallistus + t * (loppu.kallistus - alku.kallistus)});
            piirra_kone(p, siirto({x, 1.6, 0}) * matriisiksi(slerp(a, b, t)));
            piirra_kone(p, siirto({x, -1.6, 0}) * matriisiksi(e));
        }
        kuva.tallenna_ppm(argv[1]);
    }
}
