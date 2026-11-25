// Näkymäkartio kuutena tasona ja muotojen testit sitä vastaan.
#pragma once
#include "tormays.hpp"

#include <array>

// @alku tasot
struct Taso {
    Vec3 n;  // yksikkönormaali, osoittaa kartion sisään
    double d = 0;  // piste p on sisäpuolella, kun n . p + d >= 0
};
// Tasot saadaan näkymä-projektiomatriisin riveistä: leikkausavaruudessa
// piste on kartiossa, kun -w <= x, y, z <= w.
inline std::array<Taso, 6> kartion_tasot(const Mat4& np) {
    std::array<Taso, 6> tasot;
    for (int i = 0; i < 6; ++i) {
        int rivi = i / 2;
        double merkki = i % 2 ? -1 : 1;  // w + x >= 0 ja w - x >= 0
        double k[4];
        for (int j = 0; j < 4; ++j)
            k[j] = np.m[3][j] + merkki * np.m[rivi][j];
        double p = pituus({k[0], k[1], k[2]});
        tasot[i] = {{k[0] / p, k[1] / p, k[2] / p}, k[3] / p};
    }
    return tasot;  // vasen, oikea, ala, ylä, lähi, kauka
}
// @loppu tasot

// @alku testit
// Pallo on varmasti ulkona, jos se on kokonaan jonkin tason takana.
inline bool nakyy(const std::array<Taso, 6>& tasot, const Pallo& p) {
    for (const Taso& t : tasot)
        if (piste(t.n, p.keskus) + t.d < -p.sade) return false;
    return true;
}
// Laatikosta testataan vain se kulma, joka on pisimmällä tason normaalin
// suunnassa: jos sekin on takana, koko laatikko on.
inline bool nakyy(const std::array<Taso, 6>& tasot, const Laatikko& l) {
    for (const Taso& t : tasot) {
        Vec3 kulma{t.n.x >= 0 ? l.max.x : l.min.x,
                   t.n.y >= 0 ? l.max.y : l.min.y,
                   t.n.z >= 0 ? l.max.z : l.min.z};
        if (piste(t.n, kulma) + t.d < 0) return false;
    }
    return true;
}
// @loppu testit
