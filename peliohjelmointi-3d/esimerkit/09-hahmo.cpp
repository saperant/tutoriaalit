// Hahmon liike kolmioista tehdyllä radalla: loiva ja jyrkkä rinne,
// pudotus, portaat ja vino seinä. Argumenttina annetulla nimellä
// tallennetaan radan kuva (.ppm) ja hahmon reitti (.txt).
#include "yhteinen/hahmo.hpp"
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>
#include <string>
#include <vector>

// @alku rata
// Kiila: ramppi, joka nousee x-suunnassa korkeuteen h.
Verkko kiila(double x0, double x1, double h, double z0, double z1) {
    Verkko v;
    Vec3 a{x0, 0, z1}, b{x1, 0, z1}, c{x1, h, z1};
    Vec3 d{x0, 0, z0}, e{x1, 0, z0}, f{x1, h, z0};
    v.pisteet = {a, b, c, d, e, f};
    v.kolmiot = {{0, 1, 2}, {3, 5, 4}};  // päädyt
    lisaa_nelio(v, a, c, f, d);          // rinne
    lisaa_nelio(v, b, e, f, c);          // takaseinä
    return v;
}

struct Osa {
    Verkko verkko;
    Mat4 malli;
    Vari vari;
};
std::vector<Osa> rata() {
    std::vector<Osa> osat;
    auto laatikko = [&osat](Vec3 lo, Vec3 hi, Vari v,
                            const Mat4& m = yksikko()) {
        osat.push_back({laatikkoverkko(lo, hi), m, v});
    };
    laatikko({-3, -1, -5}, {42, 0, 5}, {125, 155, 112});  // lattia
    osat.push_back({kiila(4, 8, 1.5, -1.5, 1.5), yksikko(),
                    {170, 150, 110}});                     // loiva rinne
    laatikko({8, 0, -1.5}, {12, 1.5, 1.5}, {170, 150, 110});  // tasanne
    osat.push_back({kiila(16, 17.5, 3, -1.5, 1.5), yksikko(),
                    {150, 110, 100}});                     // jyrkkä rinne
    for (int i = 0; i < 5; ++i)                            // portaat
        laatikko({23 + 0.4 * i, 0, -1.5}, {25, 0.25 * (i + 1), 1.5},
                 {160, 160, 170});
    laatikko({25, 0, -1.5}, {28, 1.25, 1.5}, {160, 160, 170});
    laatikko({-0.25, 0, -4}, {0.25, 3, 4}, {185, 120, 90},  // vino seinä
             siirto({34, 0, 0}) *
                 matriisiksi(akselikulma({0, 1, 0}, rad(-35))));
    return osat;
}
// @loppu rata

int main(int argc, char** argv) {
    Maailma maailma;
    std::vector<Osa> osat = rata();
    for (const Osa& o : osat) maailma.lisaa(o.verkko, o.malli);
    maailma.valmis();

    // @alku ohjelma
    // Syöte käsikirjoituksena: kesto askelina, suunta ja hyppy.
    struct Vaihe {
        const char* nimi;
        int askelia;
        Vec3 suunta;
        bool hyppy = false;
    };
    const Vaihe vaiheet[] = {
        {"loiva rinne ylös", 150, {1, 0, 0}},
        {"tasanne ja pudotus", 90, {1, 0, 0}},
        {"jyrkkä rinne", 60, {1, 0, 0}},
        {"kierto sivulta", 45, {0, 0, 1}},
        {"ohi ja takaisin", 60, {1, 0, -0.6}},
        {"portaat", 90, {1, 0, 0}},
        {"hyppy tasanteelta", 60, {1, 0, 0}, true},
        {"vino seinä", 150, {1, 0, 0}},
    };
    // @loppu ohjelma

    // @alku ajo
    Hahmo hahmo{{1, 0.5, 0}};
    const double dt = 1.0 / 60;
    std::vector<Vec3> reitti;
    std::vector<bool> maassa;
    std::println("{:20} {:>6}  {:22} {}", "vaihe", "aika", "jalat", "tila");
    int askel_nro = 0, askelmia = 0;
    for (const Vaihe& v : vaiheet) {
        for (int i = 0; i < v.askelia; ++i, ++askel_nro) {
            Vec3 suunta = v.suunta;
            if (pituus(suunta) > 1) suunta = normalisoi(suunta);
            bool nousi = hahmo.nousee;
            askel(hahmo, maailma, suunta, v.hyppy && i == 0, dt);
            askelmia += hahmo.nousee && !nousi;
            reitti.push_back(hahmo.jalat);
            maassa.push_back(hahmo.maassa);
        }
        std::println("{:20} {:>6}  {:22} {}", v.nimi,
                     luku((askel_nro) * dt, 2), teksti(hahmo.jalat),
                     hahmo.maassa ? "maassa" : "ilmassa");
    }
    std::println("noustuja askelmia {}", askelmia);
    // @loppu ajo

    if (argc > 1) {
        std::string nimi = argv[1];
        std::ofstream f(nimi + ".txt");
        for (std::size_t i = 0; i < reitti.size(); ++i)
            f << reitti[i].x << ' ' << reitti[i].y << ' ' << reitti[i].z
              << ' ' << maassa[i] << '\n';
        Kuva kuva(840, 300, {150, 185, 225});
        Piirtaja p(kuva, perspektiivi(1 / std::tan(rad(11)), 2.8, 0.1, 200) *
                             katse({19, 22, 50}, {19, 0, 0}, {0, 1, 0}));
        for (const Osa& o : osat) piirra(p, o.verkko, o.malli, o.vari);
        for (std::size_t i = 1; i < reitti.size(); ++i)
            p.viiva(reitti[i - 1] + Vec3{0, 0.05, 0},
                    reitti[i] + Vec3{0, 0.05, 0},
                    maassa[i] ? Vari{230, 30, 30} : Vari{250, 220, 50}, true);
        for (std::size_t i = 59; i < reitti.size(); i += 90)
            piirra(p, kapseliverkko(Hahmo::SADE, Hahmo::PITUUS),
                   siirto(reitti[i]), {200, 180, 90});
        kuva.tallenna_ppm(nimi + ".ppm");
    }
}
