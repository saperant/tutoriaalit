// Verteksin matka mallista ruudulle ja kuution rautalankamalli.
#include <cstdio>

#include "yhteinen/kuva.hpp"
#include "yhteinen/malli.hpp"
#include "yhteinen/rasteri.hpp"
#include "yhteinen/vektori.hpp"

void nayta(const char* vaihe, Vec4 v) {
    std::printf("%-10s (%7.3f, %7.3f, %7.3f, %7.3f)\n", vaihe, v.x + 0.0,
                v.y + 0.0, v.z + 0.0, v.w + 0.0);
}

int main() {
    const int L = 64, K = 48;
    // @alku matriisit
    Mat4 malli = siirto(0, 0.5, 0) * kierto_y(0.8, 0.6);
    Mat4 nakyma = katse({2.4, 2, 3.2}, {0, 0.5, 0}, {0, 1, 0});
    Mat4 projektio = perspektiivi(1.5, double(L) / K, 1, 20);
    Mat4 mvp = projektio * nakyma * malli;  // oikealta vasemmalle
    // @loppu matriisit

    // @alku vaiheet
    Vec4 p = piste4({1, 1, 1});
    nayta("malli", p);
    nayta("maailma", malli * p);
    nayta("kamera", nakyma * malli * p);
    Vec4 c = mvp * p;
    nayta("leikkaus", c);
    Vec4 ndc = {c.x / c.w, c.y / c.w, c.z / c.w, 1};
    nayta("NDC", ndc);
    std::printf("ruutu      (%7.3f, %7.3f), syvyys %.3f\n",
                (ndc.x + 1) / 2 * L, (1 - ndc.y) / 2 * K, (ndc.z + 1) / 2);
    // @loppu vaiheet

    // @alku rautalanka
    Malli m = kuutio();
    Kuva kuva(L, K);
    auto ruudulle = [&](Vec3 q) {
        Vec4 v = mvp * piste4(q);
        return Vec2{(v.x / v.w + 1) / 2 * L, (1 - v.y / v.w) / 2 * K};
    };
    for (std::size_t i = 0; i < m.verteksit.size(); i += 4) {
        for (std::size_t j = 0; j < 4; ++j) {  // sivun neljä reunaa
            Vec2 a = ruudulle(m.verteksit[i + j].paikka);
            Vec2 b = ruudulle(m.verteksit[i + (j + 1) % 4].paikka);
            viiva(int(a.x), int(a.y), int(b.x), int(b.y),
                  [&](int x, int y) { kuva.aseta(x, y, {255, 255, 255}); });
        }
    }
    tilasto("rautalanka", kuva);
    ascii(kuva, 1, 2);
    // @loppu rautalanka
#ifdef KUVITUS  // make kuvat
    tallenna_ppm(kuva, "05-muunnokset.ppm");
#endif
}
