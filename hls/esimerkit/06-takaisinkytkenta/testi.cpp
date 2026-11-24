// C-testipenkki IIR-suotimelle: askelvaste ja satunnainen syöte.
#include <array>
#include <cstdio>

#include YDIN
#include "vektorit.hpp"

int main() {
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(8);
    int virheita = 0;
    for (int tapaus = 0; tapaus < 3; ++tapaus) {
        std::array<int, N> x{}, y{}, viite{};
        for (int n = 0; n < N; ++n)
            x[n] = tapaus == 0 ? 1000 : satunnainen.vali(-1000, 1000);
        int tila = 0;
        for (int n = 0; n < N; ++n) {
            tila += ((x[n] - tila) * K) >> 8;
            viite[n] = tila;
        }
        vektorit.syote("x", x);
        vektorit.syote("y", y);
        iir(x.data(), y.data());
        if (y != viite) ++virheita;
        vektorit.odotettu("y", y);
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta, virheitä %d\n",
                vektorit.tapauksia(), virheita);
    return vektorit.tallenna() && virheita == 0 ? 0 : 1;
}
