// C-testipenkki: kaikki kulmat ja satunnaisia pikseleitä.
#include <algorithm>
#include <cstdio>

#include YDIN
#include "vektorit.hpp"

int main() {
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(3);
    int virheita = 0;
    for (int tapaus = 0; tapaus < 12; ++tapaus) {
        int rgb[3];
        for (int& c : rgb)
            c = tapaus < 8 ? ((tapaus >> (&c - rgb)) & 1) * 400 - 100
                           : satunnainen.vali(0, 255);
        int viite = std::clamp((77 * rgb[0] + 150 * rgb[1] + 29 * rgb[2])
                               >> 8, 0, 255);
        int saatu = luma(rgb[0], rgb[1], rgb[2]);
        if (saatu != viite) ++virheita;
        vektorit.syote("r", rgb[0]);
        vektorit.syote("g", rgb[1]);
        vektorit.syote("b", rgb[2]);
        vektorit.paluu(saatu);
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta, virheitä %d\n",
                vektorit.tapauksia(), virheita);
    return vektorit.tallenna() && virheita == 0 ? 0 : 1;
}
