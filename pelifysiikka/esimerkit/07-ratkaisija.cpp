// Peräkkäisten impulssien ratkaisija: kierrosten määrän, lämpimän
// käynnistyksen ja Baumgarten korjauksen vaikutus. Argumenttina
// annettuun tiedostoon kirjoitetaan pinon korkeuden aikasarjat.
#include "yhteinen/maailma.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>

// @alku pino
// Kuuden metrin pino kuutioita: kappaleet 1..6 alhaalta ylös.
Maailma pino(int kierrokset, bool lammin) {
    Maailma m;
    m.asetukset.kierrokset = kierrokset;
    m.asetukset.lammin = lammin;
    m.lisaa(tee_taso());
    for (int i = 0; i < 6; ++i)
        m.lisaa(tee_laatikko(1.0, {0.5, 0.5, 0.5}, {0, 0.5 + i, 0}));
    return m;
}
// @loppu pino

// @alku mittaus
struct Tulos {
    double vajoama = 0;  // ylimmän laatikon suurin vajoama (m)
    double sivuun = 0;   // ylimmän laatikon suurin sivusiirtymä (m)
    bool kaatui = false;
};
Tulos aja(Maailma m, int askelia, std::ofstream* sarja = nullptr) {
    Tulos t;
    for (int i = 0; i < askelia; ++i) {
        m.askel();
        Vec3 p = m.kappaleet[6].sijainti;
        t.vajoama = std::max(t.vajoama, 5.5 - p.y);
        t.sivuun = std::max(t.sivuun, std::hypot(p.x, p.z));
        if (sarja) *sarja << i * m.asetukset.dt << " " << p.y << "\n";
    }
    t.kaatui = t.sivuun > 0.5;
    return t;
}
// @loppu mittaus

int main(int argc, char** argv) {
    // @alku vertailu
    std::println("kuuden kuution pino, 10 s:");
    std::println("{:>10} {:>8} {:>12} {:>12}", "kierrokset", "lämmin",
                 "vajoama", "sivuun");
    for (bool lammin : {false, true})
        for (int kierrokset : {1, 4, 10, 30}) {
            Tulos t = aja(pino(kierrokset, lammin), 600);
            std::println("{:>10} {:>8} {:>12} {:>12}", kierrokset,
                         lammin ? "kyllä" : "ei",
                         t.kaatui ? "kaatui" : luku(t.vajoama, 3) + " m",
                         t.kaatui ? "" : luku(t.sivuun, 3) + " m");
        }
    // @loppu vertailu

    // @alku baumgarte
    // Laatikko aloittaa 10 cm lattian sisällä. Korjaus työntää sen ulos
    // ja antaa samalla nopeutta, jota fysiikassa ei ole.
    std::println("\nlaatikko 10 cm lattian sisällä:");
    for (double beta : {0.1, 0.2, 0.8}) {
        Maailma m;
        m.asetukset.beta = beta;
        m.lisaa(tee_taso());
        int i = m.lisaa(tee_laatikko(1.0, {0.5, 0.5, 0.5}, {0, 0.4, 0}));
        double korkein = 0, nopein = 0;
        int askelia = 0;
        for (int a = 0; a < 240; ++a) {
            m.askel();
            const Kappale& k = m.kappaleet[i];
            korkein = std::max(korkein, k.sijainti.y - 0.5);
            nopein = std::max(nopein, k.nopeus.y);
            if (askelia == 0 && k.sijainti.y > 0.49) askelia = a + 1;
        }
        std::println("  beta {}: pinnalla {} askeleessa, suurin nopeus "
                     "{} m/s, pomppaa {} cm",
                     luku(beta, 1), askelia, luku(nopein),
                     luku(100 * korkein, 1));
    }
    // @loppu baumgarte

    if (argc > 1) {
        int n = 0;
        for (bool lammin : {false, true})
            for (int kierrokset : {4, 10}) {
                std::ofstream f(std::format("{}-{}.txt", argv[1], ++n));
                aja(pino(kierrokset, lammin), 600, &f);
            }
    }
}
