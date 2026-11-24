// Näytteenotto 4 x 4 -tekstuurista: lähin tekseli vai bilineaarinen?
#include <cstdio>

#include "yhteinen/tekstuuri.hpp"

int main() {
    // @alku naytteet
    // Tekselin (x, y) arvo on (x + 4y) / 15: vasemmalta oikealle ja
    // ylhäältä alas kasvava harmaasävy.
    Tekstuuri t{4, 4, {}};
    for (int y = 0; y < 4; ++y)
        for (int x = 0; x < 4; ++x) {
            double a = (x + 4 * y) / 15.0;
            t.t.push_back({a, a, a});
        }
    // Kuljetaan toisen tekselirivin keskeltä (v = 0.375) vaakasuoraan.
    std::printf("    u   tekseli  lähin  bilineaarinen\n");
    for (int i = 0; i <= 8; ++i) {
        double u = i / 8.0;
        Vec2 uv{u, 0.375};
        std::printf("%5.3f  %7.2f  %5.3f  %13.3f\n", u, u * 4 - 0.5,
                    t.lahin(uv).r, t.bilineaarinen(uv).r);
    }
    // @loppu naytteet

    // @alku ketju
    Mipmap m(shakki(8, 1, {0, 0, 0}, {1, 1, 1}));
    std::printf("\nmipmap 8 x 8 -shakkiruudusta:\n");
    for (const Tekstuuri& taso : m.tasot)
        std::printf("  %d x %d, ensimmäinen tekseli %.3f\n", taso.l,
                    taso.k, taso.t[0].r);
    // @loppu ketju
}
