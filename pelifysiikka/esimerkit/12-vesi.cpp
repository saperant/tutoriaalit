// Vesi korkeuskenttänä: aallon eteneminen, tilavuuden säilyminen,
// stabiilisuusraja, kelluva laatikko ja roiskeet hiukkasina.
// Argumenttina annettuun nimeen tallennetaan kuvasarja.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"
#include "yhteinen/vesi.hpp"

#include <print>

const double DT = 1.0 / 60;
const Vec3 G{0, -9.81, 0};

// @alku noste
// Laatikon noste: syrjäytetyn veden paino. Laatikko pysyy pystyssä,
// joten upoksissa oleva tilavuus on pohjan ala kertaa upotussyvyys.
// Palauttaa upotussyvyyden.
double lisaa_noste(Kappale& laatikko, const Vesi& w) {
    Vec3 e = laatikko.muoto.puolet;
    double pohja = laatikko.sijainti.y - e.y;
    double syvyys = std::clamp(
        pinta(w, laatikko.sijainti.x, laatikko.sijainti.z) - pohja, 0.0,
        2 * e.y);
    const double tiheys = 1000;  // kg/m^3
    double noste = tiheys * 9.81 * (4 * e.x * e.z) * syvyys;
    // Veden vastus hidastaa upoksissa olevaa kappaletta.
    Vec3 vastus = (-40.0 * syvyys / (2 * e.y) * massa(laatikko)) *
                  laatikko.nopeus;
    lisaa_voima(laatikko, Vec3{0, noste, 0} + vastus, laatikko.sijainti);
    return syvyys;
}
// @loppu noste

void piirra(Piirtaja& p, const Vesi& w) {
    for (int j = 0; j + 1 < w.n; ++j)
        for (int i = 0; i + 1 < w.n; ++i) {
            auto kohta = [&](int a, int b) {
                return Vec3{(a + 0.5) * w.dx, w.lue(a, b), (b + 0.5) * w.dx};
            };
            piirra_nelio(p, kohta(i, j), kohta(i, j + 1),
                         kohta(i + 1, j + 1), kohta(i + 1, j),
                         {70, 130, 200});
        }
}

// Kuvitus: allas, laatikko ja pisarat kuvaksi nimi-N.ppm.
void tallenna(const Vesi& allas, const Kappale& laatikko,
              const Pisarat& pisarat, const std::string& nimi) {
    static int kuvia = 0;
    Kuva kuva(300, 200, TAIVAS);
    Kamera kamera{{5.2, 2.6, 6.2}, {2, 0, 2}, 40, 1.5};
    Piirtaja p(kuva, nakyma_projektio(kamera));
    piirra(p, allas);
    piirra_laatikko(p, siirto(laatikko.sijainti), laatikko.muoto.puolet,
                    {190, 140, 90});
    for (std::size_t k = 0; k < pisarat.elossa; ++k)
        p.viiva(pisarat.p[k].sijainti,
                pisarat.p[k].sijainti + Vec3{0, 0.04, 0}, {240, 250, 255},
                true);
    kuva.tallenna_ppm(std::format("{}-{}.ppm", nimi, ++kuvia));
}

int main(int argc, char** argv) {
    // @alku aalto
    // Kumpu altaan keskellä leviää renkaana. Aallonharjan saapuminen
    // 1,5 metrin päähän kertoo etenemisnopeuden.
    Vesi w(40, 0.1);  // 4 m x 4 m
    w.vaimennus = 0;
    for (int j = 0; j < w.n; ++j)
        for (int i = 0; i < w.n; ++i) {
            double r2 = ((i - 20) * (i - 20) + (j - 20) * (j - 20)) * 0.01;
            w.korkeus(i, j) = 0.2 * std::exp(-r2 / (2 * 0.15 * 0.15));
        }
    double alussa = tilavuus(w);
    int saapui = 0;
    double edellinen = 0;
    for (int i = 1; i <= 75 && saapui == 0; ++i) {
        askel(w, DT);
        double h = w.korkeus(35, 20);
        if (h > 0.005 && h < edellinen) saapui = i - 1;  // harja meni ohi
        edellinen = h;
    }
    std::println("aallonharja 1,5 m:n päässä {} s:n kuluttua "
                 "(1,5 m / c = {} s)",
                 luku(saapui * DT), luku(1.5 / w.aallonnopeus));
    std::println("tilavuus {} -> {} dm^3", luku(1000 * alussa, 3),
                 luku(1000 * tilavuus(w), 3));
    // @loppu aalto

    // @alku raja
    // Stabiilisuusraja kahdessa ulottuvuudessa: c dt / dx <= 1/sqrt(2).
    for (double c : {2.0, 4.0, 4.5}) {
        Vesi koe(40, 0.1);
        koe.aallonnopeus = c;
        koe.korkeus(20, 20) = 0.2;
        double suurin = 0;
        for (int i = 0; i < 300; ++i) askel(koe, DT);
        for (double h : koe.h) suurin = std::max(suurin, std::abs(h));
        std::println("c = {} m/s: c dt/dx = {}: {}", luku(c, 1),
                     luku(c * DT / koe.dx),
                     suurin < 1 ? "vakaa" : "räjähti");
    }
    // @loppu raja

    // @alku kellunta
    // Puulaatikko (tiheys 600 kg/m^3) pudotetaan altaaseen. Osuma
    // synnyttää roiskeen ja aallon.
    Vesi allas(40, 0.1);
    allas.vaimennus = 1.0;
    Pisarat pisarat(200);
    Kappale laatikko = tee_laatikko(600 * 0.4 * 0.3 * 0.4, {0.2, 0.15, 0.2},
                                    {2.05, 1.2, 2.05});
    bool osunut = false;
    int eniten = 0;
    double upotus = 0;
    for (int i = 0; i <= 600; ++i) {
        if (argc > 1 && (i == 20 || i == 34 || i == 50 || i == 120))
            tallenna(allas, laatikko, pisarat, argv[1]);
        upotus = lisaa_noste(laatikko, allas);
        if (upotus > 0 && !osunut) {  // ensimmäinen kosketus veteen
            osunut = true;
            pisarat.synnyta(laatikko.sijainti, 120, -laatikko.nopeus.y);
            // Laatikko painaa allaan olevaa vettä alas ja ympäriltä
            // ylös. Nopeuksien summa on nolla, joten tilavuus säilyy.
            for (int dj = -3; dj <= 3; ++dj)
                for (int di = -3; di <= 3; ++di) {
                    bool alla = std::abs(di) <= 1 && std::abs(dj) <= 1;
                    allas.nopeus(20 + di, 20 + dj) += alla ? -4.0 : 0.9;
                }
        }
        integroi_nopeus(laatikko, G, DT);
        integroi_paikka(laatikko, DT);
        askel(allas, DT);
        askel(pisarat, allas, G, DT);
        eniten = std::max(eniten, static_cast<int>(pisarat.elossa));
    }
    std::println("laatikko kelluu: upoksissa {} cm (Arkhimedes: {} cm)",
                 luku(100 * upotus, 1), luku(100 * 0.3 * 0.6, 1));
    std::println("pisaroita enimmillään {}, lopussa {}", eniten,
                 pisarat.elossa);
    std::println("altaan tilavuuden muutos {} dm^3",
                 luku(1000 * tilavuus(allas), 3));
    // @loppu kellunta
}
