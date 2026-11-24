// C-testipenkki histogrammille. Syötteessä on peräkkäisiä samoja
// arvoja, koska ne paljastavat kierrosten välisen riippuvuuden.
#include <array>
#include <cstdio>

#include YDIN
#include "vektorit.hpp"

// @alku testi
int main() {
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(11);
    int virheita = 0;
    for (int tapaus = 0; tapaus < 4; ++tapaus) {
        std::array<int, N> x{};
        std::array<int, B> h{}, viite{};
        for (int i = 0; i < N; ++i) {
            // joka neljäs alkio toistaa edellisen arvon
            bool toista = i > 0 && satunnainen.vali(0, 3) == 0;
            x[i] = toista ? x[i - 1] : satunnainen.vali(0, B - 1);
            ++viite[x[i]];
        }
        vektorit.syote("x", x);
        vektorit.syote("h", h);
        hist(x.data(), h.data());
        if (h != viite) ++virheita;
        vektorit.odotettu("h", h);
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta, virheitä %d\n",
                vektorit.tapauksia(), virheita);
    return vektorit.tallenna() && virheita == 0 ? 0 : 1;
}
// @loppu testi
