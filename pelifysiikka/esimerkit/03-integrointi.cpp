// Vapaasti pyörivä kappale kolmella tavalla integroituna sekä voima,
// joka ei osu massakeskipisteeseen. Argumenttina annettuun tiedostoon
// kirjoitetaan energian ja liikemäärämomentin aikasarja ja toiseen
// kuvasarja.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>

// @alku tavat
enum class Tapa { vakio, eksplisiittinen, sailyttava, keskipiste };

// Yksi asennon askel ilman ulkoisia voimia.
void pyorita(Kappale& k, Tapa tapa, double dt) {
    if (tapa == Tapa::keskipiste) {
        integroi_paikka(k, dt);  // moottorin oma tapa (kappale.hpp)
        return;
    }
    if (tapa == Tapa::sailyttava) {
        // L pidetään vakiona, asento alkuhetken kulmanopeudella.
        Vec3 l = hitaus_maailmassa(k) * k.kulmanopeus;
        k.kierto = kierra_askel(k.kierto, k.kulmanopeus, dt);
        k.kulmanopeus = kaanteishitaus(k) * l;
        return;
    }
    if (tapa == Tapa::eksplisiittinen) {
        // Eulerin yhtälö: I dw/dt = -w x (I w), eksplisiittisenä askeleena.
        Vec3 l = hitaus_maailmassa(k) * k.kulmanopeus;
        k.kulmanopeus = k.kulmanopeus -
                        dt * (kaanteishitaus(k) * risti(k.kulmanopeus, l));
    }
    // Tapa::vakio ei muuta kulmanopeutta lainkaan.
    k.kierto = kierra_askel(k.kierto, k.kulmanopeus, dt);
}
// @loppu tavat

// @alku kappale
// Kirjan muotoinen kappale: kolme eri hitausmomenttia. Se pyörii
// keskimmäisen akselinsa ympäri, ja akseli on hieman vinossa.
Kappale kirja() {
    Kappale k = tee_laatikko(1.0, {0.6, 0.1, 0.4}, {0, 2, 0});
    k.kulmanopeus = {0.05, 0.0, 6.0};
    return k;
}
// @loppu kappale

double pyorimisenergia(const Kappale& k) {
    return 0.5 * piste(k.kulmanopeus, hitaus_maailmassa(k) * k.kulmanopeus);
}

int main(int argc, char** argv) {
    const double dt = 1.0 / 60;
    // @alku vertailu
    std::println("10 s vapaata pyörimistä, dt = 1/60 s:");
    std::println("{:16} {:>10} {:>12} {:>10}", "tapa", "E / E0",
                 "|L - L0|/L0", "kääntöjä");
    const char* nimet[] = {"vakio w", "eksplisiittinen", "L säilyy",
                           "L ja keskipiste"};
    for (Tapa tapa : {Tapa::vakio, Tapa::eksplisiittinen, Tapa::sailyttava,
                      Tapa::keskipiste}) {
        Kappale k = kirja();
        double e0 = pyorimisenergia(k);
        Vec3 l0 = hitaus_maailmassa(k) * k.kulmanopeus;
        int kaannot = 0;
        double ed = 1;
        for (int i = 0; i < 600; ++i) {
            pyorita(k, tapa, dt);
            // Pyörimisakseliksi valittu kappaleen akseli osoittaa
            // vuorotellen eteen ja taakse.
            double nyt = kierra(k.kierto, {0, 0, 1}).z;
            if (std::abs(nyt) > 0.9 && nyt * ed < 0) {
                ++kaannot;
                ed = nyt;
            }
        }
        Vec3 l = hitaus_maailmassa(k) * k.kulmanopeus;
        std::println("{:16} {:>10} {:>12} {:>10}",
                     nimet[static_cast<int>(tapa)],
                     luku(pyorimisenergia(k) / e0, 3),
                     luku(pituus(l - l0) / pituus(l0), 3), kaannot);
    }
    // @loppu vertailu

    // @alku heitto
    // Heitetty kappale: massakeskipiste lentää kuin pistemassa, vaikka
    // kappale pyörii.
    Kappale k = kirja();
    k.nopeus = {3, 4, 0};
    const Vec3 g{0, -9.81, 0};
    for (int i = 0; i < 30; ++i) {  // puoli sekuntia
        integroi_nopeus(k, g, dt);
        integroi_paikka(k, dt);
    }
    double t = 0.5;
    std::println("\nheitto 0,5 s: simuloitu   {}", teksti(k.sijainti, 3));
    std::println("              tarkka      {}",
                 teksti(Vec3{3 * t, 2 + 4 * t - 0.5 * 9.81 * t * t, 0}, 3));
    // @loppu heitto

    // @alku voima
    // Rakettimoottori lankun päässä työntää sivulle sekunnin ajan.
    Kappale lankku = tee_laatikko(4.0, {1.0, 0.1, 0.25}, {});
    for (int i = 0; i < 60; ++i) {
        Vec3 paa = maailmaan_suunta(lankku, {1, 0, 0});
        Vec3 sivu = maailmaan_suunta(lankku, {0, 0, -1});
        lisaa_voima(lankku, 2.0 * sivu, lankku.sijainti + paa);
        integroi_nopeus(lankku, {}, dt);
        integroi_paikka(lankku, dt);
    }
    std::println("\nmoottori 1 s: nopeus {}  kulmanopeus {}",
                 teksti(lankku.nopeus), teksti(lankku.kulmanopeus));
    std::println("              sijainti {}  kääntynyt {} astetta",
                 teksti(lankku.sijainti),
                 luku(aste(2 * std::acos(lankku.kierto.w)), 1));
    // @loppu voima

    if (argc > 1) {  // kuvitus: aikasarjat ja kuvasarja kääntymisestä
        std::ofstream f(std::string(argv[1]) + ".txt");
        for (Tapa tapa : {Tapa::vakio, Tapa::eksplisiittinen,
                          Tapa::sailyttava, Tapa::keskipiste}) {
            Kappale b = kirja();
            double e0 = pyorimisenergia(b);
            Vec3 l0 = hitaus_maailmassa(b) * b.kulmanopeus;
            for (int i = 0; i <= 600; ++i) {
                Vec3 l = hitaus_maailmassa(b) * b.kulmanopeus;
                f << static_cast<int>(tapa) << " " << i * dt << " "
                  << pyorimisenergia(b) / e0 << " "
                  << pituus(l - l0) / pituus(l0) << " "
                  << kierra(b.kierto, {0, 0, 1}).z << "\n";
                pyorita(b, tapa, dt);
            }
        }
        Maailma m;
        m.lisaa(kirja());
        Kamera kamera{{0, 2.6, 3.4}, {0, 2, 0}, 40, 1.0};
        int kuvia = 0;
        // Kuva kerran kierroksessa (63 askelta), jolloin vain akselin
        // kääntyminen näkyy.
        for (int i = 0; i <= 600; ++i) {
            if (i % 63 == 0 && kuvia < 10) {
                Kuva kuva(160, 160, TAIVAS);
                Piirtaja p(kuva, nakyma_projektio(kamera));
                piirra_maailma(p, m, false);
                kuva.tallenna_ppm(std::format("{}-{}.ppm", argv[1], ++kuvia));
            }
            integroi_paikka(m.kappaleet[0], dt);
        }
    }
}
