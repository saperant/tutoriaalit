// Cornellin laatikko: polunseurannan vakiokohtaus (Goral ym. 1984).
#pragma once
#include "kamera.hpp"
#include "kohtaus.hpp"

// @alku cornell
// Laatikko [0, 1]^3, avoin etupuoli kameraa kohti (z = 0). Katossa
// neliön muotoinen valo, joka säteilee alaspäin. Kamera katsoo +z:n
// suuntaan, joten x = 1 näkyy vasemmalla.
inline Kohtaus cornell(Materiaali pallo1, Materiaali pallo2) {
    Kohtaus K;
    int valkoinen = K.materiaali({});
    int punainen = K.materiaali({.vari = {0.63, 0.06, 0.05}});
    int vihrea = K.materiaali({.vari = {0.12, 0.45, 0.09}});
    int valo = K.materiaali({.vari = {0, 0, 0}, .sateily = {34, 24, 8}});
    K.suorakulmio({0, 0, 0}, {0, 0, 1}, {1, 0, 1}, {1, 0, 0}, valkoinen);
    K.suorakulmio({0, 1, 0}, {1, 1, 0}, {1, 1, 1}, {0, 1, 1}, valkoinen);
    K.suorakulmio({0, 0, 1}, {0, 1, 1}, {1, 1, 1}, {1, 0, 1}, valkoinen);
    K.suorakulmio({0, 0, 0}, {0, 1, 0}, {0, 1, 1}, {0, 0, 1}, vihrea);
    K.suorakulmio({1, 0, 0}, {1, 0, 1}, {1, 1, 1}, {1, 1, 0}, punainen);
    double y = 0.999;
    K.suorakulmio({0.38, y, 0.38}, {0.62, y, 0.38}, {0.62, y, 0.62},
                  {0.38, y, 0.62}, valo);
    K.lisaa(Pallo{{0.3, 0.2, 0.62}, 0.2}, K.materiaali(pallo1));
    K.lisaa(Pallo{{0.72, 0.15, 0.36}, 0.15}, K.materiaali(pallo2));
    return K;
}
inline Kamera cornell_kamera(int leveys, int korkeus) {
    return kamera({0.5, 0.5, -1.35}, {0.5, 0.5, 0.5}, {0, 1, 0}, 2.2,
                  leveys, korkeus);
}
// @loppu cornell
