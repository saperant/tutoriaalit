// Valaistu pallo kolmella tavalla: tasainen, Gouraud ja pikseleittäin.
#include <cstdio>

#include "yhteinen/putki.hpp"
#include "yhteinen/valo.hpp"

const int S = 48;  // yhden kuvan sivu
const Vec3 SILMA{0, 0, 3.2};
const Vec3 VALO = normalisoi({-0.5, 0.7, 0.6});  // pinnasta valoon
const Materiaali AINE{{0.02, 0.02, 0.03}, {0.8, 0.25, 0.1},
                      {0.6, 0.6, 0.6}, 40};

// @alku tasainen
// Tasainen varjostus: kolmion kaikille kärjille kolmion oma normaali.
Malli tasoita(Malli m) {
    for (const auto& k : m.kolmiot) {
        Vec3 a = m.verteksit[k[0]].paikka, b = m.verteksit[k[1]].paikka;
        Vec3 c = m.verteksit[k[2]].paikka;
        Vec3 n = normalisoi(risti(b - a, c - a));
        for (int i : k) m.verteksit[i].normaali = n;
    }
    return m;
}
// @loppu tasainen

Kohde varjosta_pallo(int tapa) {
    Mat4 malli = kierto_x(0.8, 0.6) * kierto_y(0.6, 0.8);
    Mat4 vp = perspektiivi(2.6, 1, 0.5, 10) *
              katse(SILMA, {0, 0, 0}, {0, 1, 0});
    Malli pallomalli = pallo(2);  // 128 kolmiota
    if (tapa == 0) pallomalli = tasoita(pallomalli);
    Kohde kohde(S, S, {0.01, 0.01, 0.01});
    // @alku gouraud
    // Tasainen ja Gouraud: valaistus verteksivarjostimessa, väri
    // interpoloidaan.
    auto valo_karjissa = [&](const Verteksi& v) {
        Vec3 p = xyz(malli * piste4(v.paikka));
        Vec3 n = muunna_normaali(malli, v.normaali);
        Vari c = varjosta(AINE, n, VALO, normalisoi(SILMA - p),
                          {1, 1, 1});
        return Tulos<3>{vp * piste4(p), {c.r, c.g, c.b}};
    };
    auto vari = [](const std::array<double, 3>& c, const auto&) {
        return Vari{c[0], c[1], c[2]};
    };
    // @loppu gouraud
    // @alku pikseli
    // Pikseleittäin: normaali ja paikka interpoloidaan, valaistus
    // fragmenttivarjostimessa. Normaali on normalisoitava uudelleen.
    auto valo_pikseleissa_v = [&](const Verteksi& v) {
        Vec3 p = xyz(malli * piste4(v.paikka));
        Vec3 n = muunna_normaali(malli, v.normaali);
        return Tulos<6>{vp * piste4(p), {n.x, n.y, n.z, p.x, p.y, p.z}};
    };
    auto valo_pikseleissa_f = [](const std::array<double, 6>& a,
                                 const auto&) {
        Vec3 n = normalisoi({a[0], a[1], a[2]});
        Vec3 p{a[3], a[4], a[5]};
        return varjosta(AINE, n, VALO, normalisoi(SILMA - p), {1, 1, 1});
    };
    // @loppu pikseli
    if (tapa < 2) piirra(kohde, pallomalli, valo_karjissa, vari);
    else piirra(kohde, pallomalli, valo_pikseleissa_v, valo_pikseleissa_f);
    return kohde;
}

int main() {
    // @alku vertailu
    const char* nimet[] = {"tasainen", "Gouraud", "per pikseli"};
    Kuva kaikki(3 * S + 8, S, {255, 255, 255});
    for (int tapa = 0; tapa < 3; ++tapa) {
        Kuva kuva = varjosta_pallo(tapa).kuvaksi();
        int kirkkain = 0;
        for (Rgb c : kuva.pikselit())
            kirkkain = std::max(kirkkain, kirkkaus(c));
        tilasto(nimet[tapa], kuva, koodaa({0.01, 0.01, 0.01}));
        std::printf("               kirkkain pikseli %d\n", kirkkain);
        for (int y = 0; y < S; ++y)
            for (int x = 0; x < S; ++x)
                kaikki(tapa * (S + 4) + x, y) = kuva(x, y);
    }
    tallenna_ppm(kaikki, "09-varjostus.ppm");
    ascii(kaikki, 2, 4);
    // @loppu vertailu
}
