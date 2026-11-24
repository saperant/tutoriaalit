// C-testipenkki: pienet alkuarvot, jotta välitulokset mahtuvat int:iin.
#include <cstdio>

#include YDIN
#include "vektorit.hpp"

int main() {
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(1989);
    for (int tapaus = 0; tapaus < 4; ++tapaus) {
        int x0 = satunnainen.vali(-5, 5), y0 = satunnainen.vali(-5, 5);
        int u0 = satunnainen.vali(-5, 5), dx = satunnainen.vali(1, 3);
        vektorit.syote("x0", x0);
        vektorit.syote("y0", y0);
        vektorit.syote("u0", u0);
        vektorit.syote("dx", dx);
        vektorit.paluu(diffeq(x0, y0, u0, dx));
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta\n", vektorit.tapauksia());
    return vektorit.tallenna() ? 0 : 1;
}
