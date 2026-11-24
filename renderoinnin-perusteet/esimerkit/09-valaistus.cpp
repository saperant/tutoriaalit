// Valaistusmallit lukuina: Lambert, Phong ja Blinn-Phong.
#include <cstdio>

#include "yhteinen/valo.hpp"

int main() {
    // @alku kulmat
    // Normaali osoittaa kohti katsojaa. Valo kiertää normaalin ympäri
    // x-akselin suuntaan; kulma annetaan kosinina ja sinina.
    Vec3 n{0, 0, 1};
    Vec3 v = normalisoi({-0.6, 0, 0.8});  // katsoja hieman vasemmalla
    std::printf("valon kulma  Lambert  Phong 32  Blinn 32  Blinn 128\n");
    const double kulmat[][3] = {{0, 1, 0},       {0.6, 0.8, 37},
                                {0.707, 0.707, 45}, {0.8, 0.6, 53},
                                {1, 0, 90},      {0.8, -0.6, 127}};
    for (const auto& k : kulmat) {
        Vec3 l = normalisoi({k[0], 0, k[1]});
        std::printf("%8.0f     %7.3f  %8.3f  %8.3f  %9.3f\n", k[2],
                    lambert(n, l), phong(n, l, v, 32),
                    blinn_phong(n, l, v, 32), blinn_phong(n, l, v, 128));
    }
    // @loppu kulmat
}
