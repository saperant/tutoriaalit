// C-testipenkki matriisitulolle.
#include <array>
#include <cstdio>

#include YDIN
#include "vektorit.hpp"

int main() {
    vektorit::Tallennin vektorit;
    vektorit::Satunnainen satunnainen(7);
    int virheita = 0;
    for (int tapaus = 0; tapaus < 4; ++tapaus) {
        std::array<int, N * N> a{}, b{}, c{}, viite{};
        for (int i = 0; i < N * N; ++i) {
            a[i] = satunnainen.vali(-100, 100);
            b[i] = satunnainen.vali(-100, 100);
        }
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j)
                for (int k = 0; k < N; ++k)
                    viite[i * N + j] += a[i * N + k] * b[k * N + j];
        vektorit.syote("a", a);
        vektorit.syote("b", b);
        vektorit.syote("c", c);
        matmul(a.data(), b.data(), c.data());
        if (c != viite) ++virheita;
        vektorit.odotettu("c", c);
        vektorit.tapaus_valmis();
    }
    std::printf("C-simulaatio: %d tapausta, virheitä %d\n",
                vektorit.tapauksia(), virheita);
    return vektorit.tallenna() && virheita == 0 ? 0 : 1;
}
