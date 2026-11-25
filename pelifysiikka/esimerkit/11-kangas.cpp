// Kangas kahdella tavalla: jousien jäykkyysraja ja sijaintipohjainen
// dynamiikka. Argumenttina annettuun nimeen tallennetaan kuvasarja ja
// venymän aikasarjat.
#include "yhteinen/kangas.hpp"
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>

const Vec3 G{0, -9.81, 0};
const double DT = 1.0 / 60;

// @alku ripustus
// 12 x 12 hiukkasen kangas, kiinni kahdesta kulmastaan.
Kangas ripustettu() {
    Kangas k = tee_kangas(12, {-0.5, 2, -0.5}, 1.0);
    for (Hiukkanen& h : k.hiukkaset) h.kaanteismassa = 1 / 0.01;  // 10 g
    k.hiukkaset[0].kaanteismassa = 0;
    k.hiukkaset[11].kaanteismassa = 0;
    return k;
}
// @loppu ripustus

void piirra(Piirtaja& p, const Kangas& k) {
    for (int j = 0; j + 1 < k.n; ++j)
        for (int i = 0; i + 1 < k.n; ++i) {
            int a = j * k.n + i;
            Vari v = (i + j) & 1 ? Vari{200, 90, 80} : Vari{225, 215, 200};
            const auto& h = k.hiukkaset;
            // Molemmat puolet: kangas näkyy myös takaa.
            piirra_nelio(p, h[a].sijainti, h[a + k.n].sijainti,
                         h[a + k.n + 1].sijainti, h[a + 1].sijainti, v);
            piirra_nelio(p, h[a].sijainti, h[a + 1].sijainti,
                         h[a + k.n + 1].sijainti, h[a + k.n].sijainti, v);
        }
}

// Kuvitus: kangas, pallo ja lattia kuvaksi nimi-N.ppm.
void tallenna(const Kangas& k, Vec3 keskus, double sade,
              const std::string& nimi) {
    static int kuvia = 0;
    Kuva kuva(260, 220, TAIVAS);
    Kamera kamera{{1.6, 1.9, 2.4}, {0, 0.95, 0}, 40, 260.0 / 220};
    Piirtaja p(kuva, nakyma_projektio(kamera));
    piirra_lattia(p, 4, 0.5, 0.3);
    piirra_pallo(p, siirto(keskus), sade, {90, 120, 190}, 16);
    piirra(p, k);
    kuva.tallenna_ppm(std::format("{}-{}.ppm", nimi, ++kuvia));
}

int main(int argc, char** argv) {
    // @alku jousikoe
    // Jousilla kankaan jäykkyys on jousivakio. Mitä jäykempi kangas
    // halutaan, sitä lyhyemmän askeleen integraattori vaatii.
    std::println("massa-jousi, 2 s:");
    std::println("{:>10} {:>14} {:>14}", "k (N/m)", "dt = 1/60",
                 "dt = 1/480");
    for (double jousivakio : {2.0, 8.0, 32.0, 128.0, 512.0}) {
        std::string rivi = std::format("{:>10}", luku(jousivakio, 0));
        for (int aliaskelia : {1, 8}) {
            Kangas k = ripustettu();
            double suurin = 0;
            bool hajosi = false;
            for (int i = 0; i < 120 * aliaskelia && !hajosi; ++i) {
                askel_jouset(k, jousivakio, 0.01, G, DT / aliaskelia);
                suurin = std::max(suurin, suurin_venyma(k));
                hajosi = !(suurin < 100);
            }
            rivi += std::format("{:>14}",
                                hajosi ? "räjähti"
                                       : "venyy " + luku(100 * suurin, 0) +
                                             " %");
        }
        std::println("{}", rivi);
    }
    // @loppu jousikoe

    // @alku pbdkoe
    // PBD:ssä jäykkyys tulee kierrosten määrästä, eikä mikään määrä
    // tee simulaatiosta epävakaata.
    std::println("\nPBD, 2 s, dt = 1/60 s:");
    for (int kierrokset : {1, 4, 16, 64}) {
        Kangas k = ripustettu();
        double suurin = 0, e0 = energia(k, G), e_suurin = e0;
        for (int i = 0; i < 120; ++i) {
            askel_pbd(k, kierrokset, G, DT);
            suurin = std::max(suurin, suurin_venyma(k));
            e_suurin = std::max(e_suurin, energia(k, G));
        }
        std::println("  {:>2} kierrosta: venyy {} %, energia {} -> {} J{}",
                     kierrokset, luku(100 * suurin, 0), luku(e0, 2),
                     luku(energia(k, G), 2),
                     e_suurin > e0 + 1e-9 ? " (kasvoi välillä!)" : "");
    }
    // @loppu pbdkoe

    // @alku pallo
    // Vapaa kangas putoaa pallon päälle ja jää roikkumaan sen varaan.
    Kangas k = tee_kangas(16, {-0.6, 1.6, -0.6}, 1.2);
    const Vec3 keskus{0, 1, 0};
    const double sade = 0.4;
    for (int i = 0; i < 180; ++i) {
        askel_pbd(k, 16, G, DT, keskus, sade + 0.01);
        if (argc > 1 && (i == 10 || i == 30 || i == 60 || i == 179))
            tallenna(k, keskus, sade, argv[1]);
    }
    double alin = 10, lahin = 10;
    for (const Hiukkanen& h : k.hiukkaset) {
        alin = std::min(alin, h.sijainti.y);
        lahin = std::min(lahin, pituus(h.sijainti - keskus));
    }
    std::println("\nkangas pallon päällä 3 s: alin kohta {} m, venymä {} %",
                 luku(alin), luku(100 * suurin_venyma(k), 0));
    std::println("lähin hiukkanen {} m pallon keskipisteestä (säde {} m)",
                 luku(lahin), luku(sade));
    // @loppu pallo
}
