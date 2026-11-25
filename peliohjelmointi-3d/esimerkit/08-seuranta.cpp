// Kolmannen persoonan kamera: kierto kohteen ympäri, ruutunopeudesta
// riippumaton pehmennys ja törmäys maailmaan säteellä.
// Argumenttina annetulla nimellä tallennetaan kaksi kuvaa.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/sade.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <string>
#include <vector>

// @alku kierto
struct Kiertokamera {
    Vec3 kohde;  // piste, jota kamera katsoo (hahmon olkapään korkeus)
    double kaanto = 0, nyokkays = rad(-20), etaisyys = 5;

    // Toivottu silmän paikka: kohteesta taaksepäin katselusuuntaa
    // vastaan. Paikallinen +z on kameran takana.
    Vec3 silma() const {
        return kohde +
               etaisyys * kierra(eulerista(kaanto, nyokkays, 0), {0, 0, 1});
    }
};
// @loppu kierto

// @alku pehmennys
// Eksponentiaalinen pehmennys: jäljellä olevasta erosta poistuu sama
// osuus samassa ajassa, oli askel pitkä tai lyhyt.
Vec3 pehmenna(Vec3 nyky, Vec3 tavoite, double nopeus, double dt) {
    return tavoite + std::exp(-nopeus * dt) * (nyky - tavoite);
}
// Yleinen virhe: kiinteä osuus joka ruudulla.
Vec3 pehmenna_vaarin(Vec3 nyky, Vec3 tavoite) {
    return nyky + 0.1 * (tavoite - nyky);
}
// @loppu pehmennys

// @alku tormays
// Kamera ei saa mennä seinän taakse: säde kohteesta toivottuun silmän
// paikkaan, ja silmä jää osumakohdan eteen pienen varan päähän.
double sallittu_etaisyys(const std::vector<Laatikko>& seinat, Vec3 kohde,
                         Vec3 silma, double vara = 0.3) {
    double matka = pituus(silma - kohde);
    Sade s{kohde, normalisoi(silma - kohde)};
    for (const Laatikko& l : seinat) {
        Osuma o = sade_laatikko(s, l);
        if (o.osuu) matka = std::min(matka, std::max(o.t - vara, 0.5));
    }
    return matka;
}
// @loppu tormays

void tallenna(const std::string& polku, const std::vector<Laatikko>& seinat,
              Vec3 hahmo, Vec3 silma, Vec3 kohde) {
    Kuva kuva(400, 300, {150, 185, 225});
    Piirtaja p(kuva, perspektiivi(1 / std::tan(rad(30)), 4.0 / 3, 0.1, 100) *
                         katse(silma, kohde, {0, 1, 0}));
    piirra_lattia(p, 10, 1.0, {120, 150, 110}, {135, 165, 120});
    for (const Laatikko& l : seinat)
        piirra(p, laatikkoverkko(l.min, l.max), yksikko(), {185, 120, 90});
    piirra(p, kapseliverkko(0.4, 1.8), siirto(hahmo), {200, 180, 90});
    kuva.tallenna_ppm(polku);
}

int main(int argc, char** argv) {
    // @alku ruutunopeus
    // Kohde liikkuu 5 m/s kaksi sekuntia; kamera seuraa pehmennettynä.
    std::println("kameran jälkeenjääneisyys kahden sekunnin jälkeen:");
    for (int hz : {30, 60, 120}) {
        double dt = 1.0 / hz;
        Vec3 kohde, oikein, vaarin;
        for (int i = 0; i < 2 * hz; ++i) {
            kohde.x += 5 * dt;
            oikein = pehmenna(oikein, kohde, 6, dt);
            vaarin = pehmenna_vaarin(vaarin, kohde);
        }
        std::println("  {:3} Hz: eksponentiaalinen {} m, kiinteä osuus {} m",
                     hz, luku(kohde.x - oikein.x), luku(kohde.x - vaarin.x));
    }
    // @loppu ruutunopeus

    // @alku kavely
    // Hahmo kävelee seinän editse; kamera on sen takana (+z-puolella).
    std::vector<Laatikko> seinat = {{{-2.5, 0, 2.5}, {3.5, 3, 3}}};
    Kiertokamera kamera;
    std::println("\nhahmon x   toivottu etäisyys   sallittu etäisyys");
    for (int i = 0; i <= 8; ++i) {
        Vec3 hahmo{-4.0 + i, 0, 0};
        kamera.kohde = hahmo + Vec3{0, 1.5, 0};
        double sallittu = sallittu_etaisyys(seinat, kamera.kohde,
                                            kamera.silma());
        std::println("{:>8} {:>19} {:>19}", luku(hahmo.x, 1),
                     luku(kamera.etaisyys), luku(sallittu));
        if (argc > 1 && i == 4) {
            Vec3 suunta = normalisoi(kamera.silma() - kamera.kohde);
            tallenna(std::string(argv[1]) + "-1.ppm", seinat, hahmo,
                     kamera.silma(), kamera.kohde);
            tallenna(std::string(argv[1]) + "-2.ppm", seinat, hahmo,
                     kamera.kohde + sallittu * suunta, kamera.kohde);
        }
    }
    // @loppu kavely
}
