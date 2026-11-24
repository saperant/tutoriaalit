// Barysentriset koordinaatit: kärkien värit interpoloidaan kolmion yli.
#include <cstdio>

#include "yhteinen/kuva.hpp"
#include "yhteinen/rasteri.hpp"

int main() {
    // @alku painot
    Vec2 a{4, 44}, b{60, 36}, c{24, 4};
    for (Vec2 p : {a, Vec2{32, 28}, Vec2{(4 + 60 + 24) / 3.0, 28},
                   Vec2{50, 10}}) {
        Bary w = barysentriset(a, b, c, p);
        w = {w.l0 + 0.0, w.l1 + 0.0, w.l2 + 0.0};  // -0.000 pois
        std::printf("p = (%5.2f, %5.2f): %6.3f %6.3f %6.3f  summa %.3f%s\n",
                    p.x, p.y, w.l0, w.l1, w.l2, w.l0 + w.l1 + w.l2,
                    w.l0 < 0 || w.l1 < 0 || w.l2 < 0 ? "  ulkona" : "");
    }
    // @loppu painot

    // @alku vari
    Vari ka{1, 0, 0}, kb{0, 1, 0}, kc{0, 0, 1};
    Kuva kuva(64, 48);
    long n = 0;
    rasteroi(a, b, c, 64, 48, [&](int x, int y, Bary w) {
        kuva(x, y) = koodaa(w.l0 * ka + w.l1 * kb + w.l2 * kc);
        ++n;
    });
    Rgb keski = kuva(29, 28);
    double ala = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    std::printf("pikseleitä %ld, ala %.1f\n", n, std::abs(ala) / 2);
    std::printf("keskikohdan (29, 28) väri (%d, %d, %d)\n", keski.r,
                keski.g, keski.b);
    tallenna_ppm(kuva, "04-barysentrinen.ppm");
    tilasto("kolmio", kuva);
    ascii(kuva, 2, 4);
    // @loppu vari
}
