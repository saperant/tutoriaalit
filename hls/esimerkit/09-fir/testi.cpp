// C-testipenkki FIR-suotimelle: vertaa suoraan konvoluutioon.
#include <array>
#include <cstdio>
#include <vector>

#include YDIN
#include "vektorit.hpp"

// @alku testi
int main() {
    const std::array<int, T> kertoimet = {-3, 12, 37, 82, 82, 37, 12, -3};
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(5);
    int virheita = 0;
    for (int tapaus = 0; tapaus < 3; ++tapaus) {
        std::vector<int> naytteet(PITUUS), viite(PITUUS);
        virta<int> x, y;
        for (int n = 0; n < PITUUS; ++n) {
            naytteet[n] = satunnainen.vali(-2048, 2047);
            x.write(naytteet[n]);
        }
        for (int n = 0; n < PITUUS; ++n) {
            int s = 0;
            for (int k = 0; k < T && k <= n; ++k)
                s += kertoimet[k] * naytteet[n - k];
            viite[n] = s >> 8;
        }
        fir(x, y);
        std::vector<int> tulos = y.tyhjenna();
        if (tulos != viite || !x.empty()) ++virheita;
        vektorit.syote("x", naytteet);
        vektorit.odotettu("y", tulos);
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta, virheitä %d\n",
                vektorit.tapauksia(), virheita);
    return vektorit.tallenna() && virheita == 0 ? 0 : 1;
}
// @loppu testi
