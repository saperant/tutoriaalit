// C-testipenkki: vertaa ydintä viitetoteutukseen ja kirjaa testivektorit
// RTL-simulaatiota varten.
#include <array>
#include <cstdio>
#include <numeric>

#include YDIN
#include "vektorit.hpp"

// @alku testi
int main() {
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(2026);
    int virheita = 0;
    for (int tapaus = 0; tapaus < 4; ++tapaus) {
        std::array<int, N> a{}, b{};
        for (int i = 0; i < N; ++i) {
            a[i] = satunnainen.vali(-1000, 1000);
            b[i] = satunnainen.vali(-1000, 1000);
        }
        int odotettu = std::inner_product(a.begin(), a.end(), b.begin(), 0);
        int saatu = mac(a.data(), b.data());
        if (saatu != odotettu) {
            std::printf("tapaus %d: %d, odotettiin %d\n", tapaus, saatu,
                        odotettu);
            ++virheita;
        }
        vektorit.syote("a", a);
        vektorit.syote("b", b);
        vektorit.paluu(saatu);
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta, virheitä %d\n",
                vektorit.tapauksia(), virheita);
    return vektorit.tallenna() && virheita == 0 ? 0 : 1;
}
// @loppu testi
