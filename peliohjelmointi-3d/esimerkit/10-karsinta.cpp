// Näkyvyyskarsinta: näkymäkartion tasot, pallojen testaus yksitellen ja
// hierarkkisesti BVH:lla. Argumenttina annetulla nimellä tallennetaan
// kameran kuva (.ppm) ja kappaleiden tila ylhäältä katsottuna (.txt).
#include "yhteinen/bvh.hpp"
#include "yhteinen/kartio.hpp"
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    // @alku kentta
    // 2000 palloa 200 x 200 metrin kentällä näennäissatunnaisissa
    // paikoissa.
    unsigned tila = 2024;
    auto satunnainen = [&tila]() {
        tila = tila * 1664525u + 1013904223u;
        return (tila >> 8) / 16777216.0;
    };
    std::vector<Pallo> pallot;
    std::vector<Laatikko> laatikot;
    for (int i = 0; i < 2000; ++i) {
        double r = 0.4 + 0.6 * satunnainen();
        pallot.push_back({{-100 + 200 * satunnainen(), r,
                           -100 + 200 * satunnainen()}, r});
        laatikot.push_back(ymparys(pallot.back()));
    }
    Bvh puu = rakenna_bvh(laatikot);
    // @loppu kentta

    // @alku kamera
    const double f = 1 / std::tan(rad(30));  // pystykulma 60 astetta
    Mat4 projektio = perspektiivi(f, 16.0 / 9, 0.1, 60);  // kauas 60 m
    Vec3 silma{0, 2, 0};
    std::println("{:>6} {:>18} {:>15} {:>18}", "kääntö",
                 "testejä yksitellen", "näkyviä palloja", "testejä BVH:lla");
    for (int kulma : {0, 45, 90, 180, 270}) {
        Vec3 eteen = kierra(akselikulma({0, 1, 0}, rad(kulma)), {0, 0, -1});
        auto tasot = kartion_tasot(projektio *
                                   katse(silma, silma + eteen, {0, 1, 0}));
        int nakyvia = 0;
        for (const Pallo& p : pallot) nakyvia += nakyy(tasot, p);
        // Hierarkkinen karsinta: kokonainen haara hylätään yhdellä testillä.
        BvhLaskuri laskuri;
        int bvh_nakyvia = 0;
        kay_lapi(
            puu, [&](const Laatikko& l) { return nakyy(tasot, l); },
            [&](int i) { bvh_nakyvia += nakyy(tasot, pallot[i]); },
            &laskuri);
        std::println("{:>6} {:>18} {:>15} {:>18}{}", kulma, pallot.size(),
                     nakyvia, laskuri.solmuja + laskuri.kohteita,
                     bvh_nakyvia == nakyvia ? "" : "  ERI TULOS");
    }
    // @loppu kamera

    if (argc > 1) {
        std::string nimi = argv[1];
        Vec3 eteen = kierra(akselikulma({0, 1, 0}, rad(45)), {0, 0, -1});
        Mat4 np = projektio * katse(silma, silma + eteen, {0, 1, 0});
        auto tasot = kartion_tasot(np);
        std::ofstream t(nimi + ".txt");
        for (const Pallo& p : pallot)
            t << p.keskus.x << ' ' << p.keskus.z << ' ' << p.sade << ' '
              << nakyy(tasot, p) << '\n';
        Kuva kuva(560, 315, {150, 185, 225});
        Piirtaja piirtaja(kuva, np);
        piirra_lattia(piirtaja, 50, 2.0, {120, 150, 110}, {135, 165, 120});
        for (std::size_t i = 0; i < pallot.size(); ++i)
            if (nakyy(tasot, pallot[i]))
                piirra(piirtaja, palloverkko(pallot[i].sade, 10),
                       siirto(pallot[i].keskus),
                       i % 3 == 0   ? Vari{190, 110, 80}
                       : i % 3 == 1 ? Vari{90, 120, 190}
                                    : Vari{200, 180, 90});
        kuva.tallenna_ppm(nimi + ".ppm");
    }
}
