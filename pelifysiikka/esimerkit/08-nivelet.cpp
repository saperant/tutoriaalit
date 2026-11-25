// Nivelet: heilurin jakso analyyttista arvoa vastaan, ketju ja sen
// venyminen sekä sarana. Argumenttina annettuun nimeen tallennetaan
// kuvasarja ketjusta ja energian aikasarja.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>

const double G = 9.81;

// @alku jakso
// Heilurin jakso: aika peräkkäisten samansuuntaisten keskikohdan
// ylitysten välillä, keskiarvona usealta heilahdukselta.
double jakso(Maailma& m, int kappale, double kesto) {
    double edellinen = m.kappaleet[kappale].sijainti.x;
    double eka = 0, vika = 0;
    int ylityksia = 0;
    for (int i = 0; i * m.asetukset.dt < kesto; ++i) {
        m.askel();
        double x = m.kappaleet[kappale].sijainti.x;
        if (edellinen < 0 && x >= 0) {
            // Ylityshetki lineaarisella interpoloinnilla askeleen sisältä.
            double t = (i + edellinen / (edellinen - x)) * m.asetukset.dt;
            if (ylityksia++ == 0) eka = t;
            vika = t;
        }
        edellinen = x;
    }
    return (vika - eka) / (ylityksia - 1);
}
// @loppu jakso

// @alku heilurit
// Pistemäinen paino metrin langassa: etäisyysrajoite kattoon.
Maailma lankaheiluri(double kulma) {
    Maailma m;
    int katto = m.lisaa(tee_seina({0.5, 0.05, 0.5}, {0, 3.05, 0}));
    int paino = m.lisaa(tee_pallo(
        1.0, 0.05, {std::sin(kulma), 3 - std::cos(kulma), 0}));
    m.nivelet.push_back(etaisyysnivel(m.kappaleet, katto, paino, {0, 3, 0},
                                      m.kappaleet[paino].sijainti));
    return m;
}
// Metrin tanko, joka roikkuu päästään pallonivelessä.
Maailma tankoheiluri(double kulma) {
    Maailma m;
    int katto = m.lisaa(tee_seina({0.5, 0.05, 0.5}, {0, 3.05, 0}));
    Kappale tanko = tee_laatikko(1.0, {0.02, 0.5, 0.02}, {});
    tanko.kierto = akselikulma({0, 0, 1}, kulma);
    tanko.sijainti = Vec3{0, 3, 0} + kierra(tanko.kierto, {0, -0.5, 0});
    int t = m.lisaa(tanko);
    m.nivelet.push_back(pallonivel(m.kappaleet, katto, t, {0, 3, 0}));
    return m;
}
// @loppu heilurit

// @alku ketju
// Viisi lenkkiä pallonivelillä peräkkäin, aluksi vaakasuorassa.
Maailma ketju(double beta, int kierrokset) {
    Maailma m;
    m.asetukset.beta = beta;
    m.asetukset.kierrokset = kierrokset;
    int edellinen = m.lisaa(tee_seina({0.5, 0.05, 0.5}, {0, 3.05, 0}));
    for (int i = 0; i < 5; ++i) {
        int lenkki = m.lisaa(
            tee_laatikko(0.5, {0.25, 0.05, 0.05}, {0.25 + 0.5 * i, 3, 0}));
        m.nivelet.push_back(
            pallonivel(m.kappaleet, edellinen, lenkki, {0.5 * i, 3.0, 0}));
        edellinen = lenkki;
    }
    return m;
}
// Suurin rako nivelen kiinnityspisteiden välillä.
double suurin_rako(const Maailma& m) {
    double suurin = 0;
    for (const Nivel& n : m.nivelet)
        suurin = std::max(
            suurin, pituus(maailmaan(m.kappaleet[n.b], n.kiinnitys_b) -
                           maailmaan(m.kappaleet[n.a], n.kiinnitys_a)));
    return suurin;
}
// @loppu ketju

int main(int argc, char** argv) {
    // @alku jaksot
    const double lanka = 2 * PII * std::sqrt(1.0 / G);
    const double tanko = 2 * PII * std::sqrt(2.0 / (3 * G));
    for (double dt : {1.0 / 60, 1.0 / 240}) {
        Maailma a = lankaheiluri(0.1), b = tankoheiluri(0.1);
        a.asetukset.dt = b.asetukset.dt = dt;
        std::println("dt = 1/{} s:", luku(1 / dt, 0));
        std::println("  lankaheiluri {} s (kaava {} s)",
                     luku(jakso(a, 1, 20), 3), luku(lanka, 3));
        std::println("  tankoheiluri {} s (kaava {} s)",
                     luku(jakso(b, 1, 20), 3), luku(tanko, 3));
    }
    // @loppu jaksot

    // @alku ketjutulos
    struct Koe {
        double beta;
        int kierrokset, aliaskelia;
    };
    std::println("\nviiden lenkin ketju, 10 s:");
    std::println("{:>5} {:>10} {:>10} {:>12} {:>10} {:>10}", "beta",
                 "kierrokset", "aliaskelia", "suurin rako", "lopussa",
                 "energia");
    for (Koe koe : {Koe{0.0, 10, 1}, Koe{0.2, 10, 1}, Koe{0.2, 40, 1},
                    Koe{0.2, 10, 4}}) {
        Maailma m = ketju(koe.beta, koe.kierrokset);
        m.asetukset.dt = 1.0 / (60 * koe.aliaskelia);
        double rako = 0;
        for (int i = 0; i < 600 * koe.aliaskelia; ++i) {
            m.askel();
            rako = std::max(rako, suurin_rako(m));
        }
        std::println("{:>5} {:>10} {:>10} {:>9} mm {:>7} mm {:>8} J",
                     luku(koe.beta, 1), koe.kierrokset, koe.aliaskelia,
                     luku(1000 * rako, 1), luku(1000 * suurin_rako(m), 1),
                     luku(energia(m), 1));
    }
    // @loppu ketjutulos

    // @alku sarana
    // Ovi saranalla pystyakselin ympäri. Alkunopeudessa on myös
    // kiertoa, jota sarana ei salli.
    Maailma m;
    m.asetukset.painovoima = {};
    int karmi = m.lisaa(tee_seina({0.05, 1, 0.05}, {-0.05, 1, 0}));
    int ovi = m.lisaa(tee_laatikko(5.0, {0.5, 1, 0.03}, {0.5, 1, 0}));
    m.nivelet.push_back(
        sarana(m.kappaleet, karmi, ovi, {0, 1, 0}, {0, 1, 0}));
    m.kappaleet[ovi].kulmanopeus = {0.5, 2, 0.3};
    for (int i = 0; i < 120; ++i) m.askel();
    std::println("\novi 2 s: kulmanopeus {}  saranan rako {} mm",
                 teksti(m.kappaleet[ovi].kulmanopeus),
                 luku(1000 * suurin_rako(m), 2));
    // @loppu sarana

    if (argc > 1) {
        Maailma k = ketju(0.2, 10);
        Kamera kamera{{1.0, 2.0, 5.2}, {0.9, 1.75, 0}, 36, 1.3};
        std::ofstream f(std::string(argv[1]) + ".txt");
        int kuvia = 0;
        for (int i = 0; i <= 600; ++i) {
            if (i % 14 == 0 && kuvia < 6)
                tallenna_kuva(k, kamera, argv[1], ++kuvia, 260, false);
            f << i * k.asetukset.dt << " " << energia(k) << " "
              << suurin_rako(k) << "\n";
            k.askel();
        }
    }
}
