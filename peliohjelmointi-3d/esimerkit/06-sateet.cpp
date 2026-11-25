// Säteenheitto: kohteen valinta hiirellä ja nopean ammuksen pyyhkäisy.
// Argumenttina annettuun tiedostoon piirretään kohtaus ja osumat.
#include "yhteinen/mallit.hpp"
#include "yhteinen/sade.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <string>
#include <vector>

// @alku kamera
struct Kamera {
    Vec3 silma, kohde;
    double f;  // 1 / tan(fov/2)
    int leveys, korkeus;
};
// Säde kamerasta pikselin keskipisteen läpi. Suunta kootaan kameran
// akseleista, joten käänteismatriisia ei tarvita.
Sade sade_pikselista(const Kamera& k, int px, int py) {
    Vec3 eteen = normalisoi(k.kohde - k.silma);
    Vec3 oikea = normalisoi(risti(eteen, {0, 1, 0}));
    Vec3 ylos = risti(oikea, eteen);
    double suhde = static_cast<double>(k.leveys) / k.korkeus;
    double x = (2 * (px + 0.5) / k.leveys - 1) * suhde / k.f;
    double y = (1 - 2 * (py + 0.5) / k.korkeus) / k.f;
    return {k.silma, normalisoi(eteen + x * oikea + y * ylos)};
}
// @loppu kamera

// @alku maailma
struct Maailma {
    Pallo pallo{{2.5, 0.8, 1}, 0.8};
    Laatikko laatikko{{-1.5, 0, -1}, {0.5, 2, 1}};
    Laatikko torni{{-4, 0, -5}, {-3, 4, -4}};
    Kolmio lattia[2] = {{{-8, 0, 8}, {8, 0, 8}, {8, 0, -8}},
                        {{-8, 0, 8}, {8, 0, -8}, {-8, 0, -8}}};
};
// Lähin osuma: jokainen kohde testataan, ja pienin t voittaa.
Osuma lahin_osuma(const Maailma& m, const Sade& s, std::string& nimi) {
    Osuma paras;
    auto kokeile = [&](const Osuma& o, const char* kohde) {
        if (o.osuu && (!paras.osuu || o.t < paras.t)) {
            paras = o;
            nimi = kohde;
        }
    };
    kokeile(sade_pallo(s, m.pallo), "pallo");
    kokeile(sade_laatikko(s, m.laatikko), "laatikko");
    kokeile(sade_laatikko(s, m.torni), "torni");
    for (const Kolmio& k : m.lattia) kokeile(sade_kolmio(s, k), "lattia");
    return paras;
}
// @loppu maailma

int main(int argc, char** argv) {
    Maailma maailma;
    Kamera kamera{{6, 4, 8}, {0.5, 1, 0}, 1 / std::tan(rad(30)), 480, 300};
    const int pikselit[][2] = {{272, 172}, {210, 150}, {226, 90},
                               {360, 250}, {60, 30}};

    // @alku valinta
    std::println("Valinta hiirellä:");
    std::vector<Vec3> osumat, normaalit;
    for (auto [px, py] : pikselit) {
        Sade s = sade_pikselista(kamera, px, py);
        std::string nimi = "ei mitään";
        Osuma o = lahin_osuma(maailma, s, nimi);
        if (!o.osuu) {
            std::println("  pikseli ({:3}, {:3}): {}", px, py, nimi);
            continue;
        }
        std::println("  pikseli ({:3}, {:3}): {:9} etäisyys {:>5}  "
                     "normaali {}",
                     px, py, nimi, luku(o.t), teksti(o.normaali));
        osumat.push_back(kohta(s, o.t));
        normaalit.push_back(o.normaali);
    }
    // @loppu valinta

    // @alku pyyhkaisy
    // Ammus (säde 0,1 m) lentää 60 m/s kohti 0,2 m paksua seinää.
    // Yhden askeleen matka on metri, joten paikkojen vertailu hyppää
    // seinän yli. Pyyhkäisy on säde seinää vastaan, jota on kasvatettu
    // ammuksen säteellä joka suuntaan.
    Laatikko seina{{-2, 0, -0.1}, {2, 3, 0.1}};
    Pallo ammus{{0.3, 1.5, 3.55}, 0.1};
    Vec3 nopeus{0, 0, -60};
    const double dt = 1.0 / 60;
    std::println("\nNopea ammus ja ohut seinä:");
    for (int askel = 1; askel <= 5; ++askel) {
        Vec3 r{ammus.sade, ammus.sade, ammus.sade};
        Laatikko kasvatettu{seina.min - r, seina.max + r};
        Sade liike{ammus.keskus, normalisoi(nopeus)};
        Osuma o = sade_laatikko(liike, kasvatettu);
        ammus.keskus = ammus.keskus + dt * nopeus;
        bool paikka_osuu = tormaa(ammus, seina).osuu;
        bool pyyhkaisy_osuu = o.osuu && o.t <= pituus(dt * nopeus);
        std::println("  askel {}: z = {:>5}  paikkatesti {:5}  pyyhkäisy {}",
                     askel, luku(ammus.keskus.z),
                     paikka_osuu ? "osuu" : "ei",
                     pyyhkaisy_osuu
                         ? std::format("osuu matkalla {} m", luku(o.t))
                         : "ei");
    }
    // @loppu pyyhkaisy

    if (argc > 1) {
        Kuva kuva(kamera.leveys, kamera.korkeus, {150, 185, 225});
        Piirtaja p(kuva,
                   perspektiivi(kamera.f, 1.6, 0.1, 100) *
                       katse(kamera.silma, kamera.kohde, {0, 1, 0}));
        piirra_lattia(p, 8, 1.0, {120, 150, 110}, {135, 165, 120});
        piirra(p, palloverkko(maailma.pallo.sade, 16),
               siirto(maailma.pallo.keskus), {90, 120, 190});
        piirra(p, laatikkoverkko(maailma.laatikko.min, maailma.laatikko.max),
               yksikko(), {190, 110, 80});
        piirra(p, laatikkoverkko(maailma.torni.min, maailma.torni.max),
               yksikko(), {200, 180, 90});
        for (std::size_t i = 0; i < osumat.size(); ++i) {
            p.viiva(osumat[i], osumat[i] + 0.9 * normaalit[i], {230, 30, 30},
                    true);
            piirra(p, palloverkko(0.08, 6), siirto(osumat[i]),
                   {255, 240, 80});
        }
        kuva.tallenna_ppm(argv[1]);
    }
}
