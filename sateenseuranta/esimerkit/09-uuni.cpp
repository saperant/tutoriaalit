// Valkoisen uunin testi: tasaisesti valaistu ympäristö, jossa
// energiaa säilyttävä valkoinen pinta katoaa taustaan.
#include <cstdio>

#include "yhteinen/kamera.hpp"
#include "yhteinen/polku.hpp"

const int S = 24;  // yhden paneelin sivu

// @alku uuni
// Pallo yksin ympäristössä, jonka radianssi on 1 joka suunnasta.
// Palauttaa pallon sisäpikseleiden keskiarvon ja piirtää paneelin.
double uuni(const Materiaali& m, Kehys& kuva, int paneeli) {
    Kohtaus K;
    K.tausta = {1, 1, 1};
    Pallo pallo{{0, 0, 0}, 1};
    K.lisaa(pallo, K.materiaali(m));
    Kamera k = kamera({0, 0, -5}, {0, 0, 0}, {0, 1, 0}, 4, S, S);
    Laskuri laskuri;
    Kehys p = renderoi(K, k, 64, 5, {}, laskuri);
    double summa = 0;
    int n = 0;
    for (int y = 0; y < S; ++y)
        for (int x = 0; x < S; ++x) {
            kuva(paneeli * S + x, y) = p(x, y);
            bool sisalla = true;       // kaikki kulmat osuvat palloon
            for (int c = 0; c < 4; ++c)
                sisalla &= leikkaa_pallo(pallo, k.sade(x + c % 2, y + c / 2),
                                         0, AARETON) < AARETON;
            if (sisalla) {
                summa += luminanssi(p(x, y));
                ++n;
            }
        }
    return summa / n;
}
// @loppu uuni

int main() {
    // @alku main
    const Materiaali aineet[] = {
        {.vari = {1, 1, 1}},                 // Lambert
        {.laji = Materiaali::karhea, .vari = {1, 1, 1}, .karheus = 0.5},
        {.laji = Materiaali::karhea, .vari = {1, 1, 1}, .karheus = 0.3,
         .metalli = 1},
        {.laji = Materiaali::karhea, .vari = {1, 1, 1}, .karheus = 1,
         .metalli = 1}};
    const char* nimet[] = {"Lambert", "eriste 0.5", "metalli 0.3",
                           "metalli 1.0"};
    Kehys kuva(4 * S, S);
    for (int i = 0; i < 4; ++i) {
        double ka = uuni(aineet[i], kuva, i);
        otsake(nimet[i], 13);
        std::printf("keskiarvo %.3f\n", ka);
    }
    ascii(kuva, 2, 4);
    tallenna_ppm(kuva, "09-uuni.ppm");
    // @loppu main
}
