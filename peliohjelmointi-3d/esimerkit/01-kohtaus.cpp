// Ensimmäinen kohtaus: kappaleet, kamera ja kappaleiden paikat ruudulla.
// Argumenttina annettuun tiedostoon tallennetaan kohtauksen kuva.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <vector>

// @alku kappale
// Pelin tila on dataa: kappaleella on muunnos, ja muoto on resurssi.
struct Kappale {
    const char* nimi;
    Muunnos muunnos;  // sijainti, kierto ja skaala maailmassa
    Verkko verkko;
    Vari vari;
};
// @loppu kappale

int main(int argc, char** argv) {
    // @alku kohtaus
    std::vector<Kappale> kappaleet = {
        {"laatikko",
         {{0, 1, 0}, akselikulma({0, 1, 0}, rad(30)), {1, 1, 1}},
         laatikkoverkko({-1, -1, -1}, {1, 1, 1}),
         {190, 110, 80}},
        {"pallo", {{3, 0.7, 2}, {}, {1, 1, 1}}, palloverkko(0.7),
         {90, 120, 190}},
        {"torni",
         {{-3, 0, -4}, {}, {1, 4, 1}},
         laatikkoverkko({-0.5, 0, -0.5}, {0.5, 1, 0.5}),
         {200, 180, 90}},
    };
    const int leveys = 480, korkeus = 300;
    Vec3 silma{6, 4, 8};
    Mat4 nakyma = katse(silma, {0.5, 1, 0}, {0, 1, 0});
    Mat4 projektio = perspektiivi(1 / std::tan(rad(30)),
                                  static_cast<double>(leveys) / korkeus,
                                  0.1, 100);
    // @loppu kohtaus

    // @alku ruudulle
    for (const Kappale& k : kappaleet) {
        Vec3 p = k.muunnos.sijainti;
        Vec4 c = projektio * (nakyma * Vec4{p.x, p.y, p.z, 1});
        int x = static_cast<int>((c.x / c.w * 0.5 + 0.5) * leveys);
        int y = static_cast<int>((0.5 - c.y / c.w * 0.5) * korkeus);
        std::println("{:9} maailmassa {:22} ruudulla ({:3}, {:3}) "
                     "etäisyys {}",
                     k.nimi, teksti(p), x, y, luku(c.w));
    }
    // @loppu ruudulle

    if (argc > 1) {
        Kuva kuva(leveys, korkeus, {150, 185, 225});
        Piirtaja piirtaja(kuva, projektio * nakyma);
        piirra_lattia(piirtaja, 8, 1.0, {120, 150, 110}, {135, 165, 120});
        for (const Kappale& k : kappaleet)
            piirra(piirtaja, k.verkko, matriisi(k.muunnos), k.vari);
        // Maailman akselit: x punainen, y vihreä, z sininen.
        piirtaja.viiva({0, 0.01, 0}, {3, 0.01, 0}, {220, 40, 40}, true);
        piirtaja.viiva({0, 0, 0}, {0, 3, 0}, {40, 180, 40}, true);
        piirtaja.viiva({0, 0.01, 0}, {0, 0.01, 3}, {40, 70, 230}, true);
        kuva.tallenna_ppm(argv[1]);
    }
}
