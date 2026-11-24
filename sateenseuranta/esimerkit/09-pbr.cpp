// Fysikaalinen materiaalimalli: metalli ja eriste karheuden mukaan.
#include <cstdio>

#include "yhteinen/kamera.hpp"
#include "yhteinen/polku.hpp"

#ifdef KUVITUS   // make kuvat: suurempi kuva tähän dokumenttiin
const int L = 320, K = 80, N = 256;
#else
const int L = 80, K = 20, N = 16;
#endif

// @alku kohtaus
// Viisi palloa riviin, karheus 0.1 ... 0.9 vasemmalta oikealle.
// Yläpuolella suorakulmainen valo, alla harmaa lattia.
Kohtaus rivi(Materiaali pohja) {
    Kohtaus K_;
    K_.tausta = {0.03, 0.035, 0.05};
    int lattia = K_.materiaali({.vari = {0.4, 0.4, 0.4}});
    int valo = K_.materiaali({.vari = {0, 0, 0}, .sateily = {6, 6, 6}});
    K_.suorakulmio({-9, 0, -9}, {-9, 0, 9}, {9, 0, 9}, {9, 0, -9}, lattia);
    K_.suorakulmio({-2, 3, -2}, {2, 3, -2}, {2, 3, 0}, {-2, 3, 0}, valo);
    for (int i = 0; i < 5; ++i) {
        Materiaali m = pohja;
        m.karheus = 0.1 + 0.2 * i;
        K_.lisaa(Pallo{{2.0 - i, 0.4, 0}, 0.4}, K_.materiaali(m));
    }
    return K_;
}
// @loppu kohtaus

int main() {
    // @alku main
    Materiaali kulta{.laji = Materiaali::karhea,
                     .vari = {1.0, 0.78, 0.34}, .metalli = 1};
    Materiaali muovi{.laji = Materiaali::karhea,
                     .vari = {0.7, 0.08, 0.05}, .metalli = 0};
    Kamera k = kamera({0, 1.2, -6}, {0, 0.4, 0}, {0, 1, 0}, 9, L, K);
    Kehys kuva(L, 2 * K);
    for (int r = 0; r < 2; ++r) {
        Laskuri laskuri;
        Kehys p = renderoi(rivi(r == 0 ? kulta : muovi), k, N, 6, {},
                           laskuri);
        raportti(r == 0 ? "kulta" : "punainen muovi", p);
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x) kuva(x, r * K + y) = p(x, y);
    }
    ascii(kuva, 2, 4);
    tallenna_ppm(kuva, "09-pbr.ppm");
    // @loppu main
}
