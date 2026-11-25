// Laaja vaihe kolmioverkolle: BVH:n rakennus, säteen läpikäynti ja
// alueen kysely verrattuna kaikkien kolmioiden testaamiseen.
// Argumenttina annettuun tiedostoon piirretään maasto ja puun laatikot.
#include "yhteinen/bvh.hpp"
#include "yhteinen/maasto.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <vector>

// @alku syvyys
int syvyys(const Bvh& puu, int solmu = 0) {
    const BvhSolmu& s = puu.solmut[solmu];
    if (s.maara > 0) return 1;
    return 1 + std::max(syvyys(puu, s.vasen), syvyys(puu, s.oikea));
}
// @loppu syvyys

int main(int argc, char** argv) {
    // @alku maailma
    Verkko maasto = maastoverkko(48, 24.0);
    std::vector<Kolmio> kolmiot = kolmioiksi(maasto, yksikko());
    for (const Laatikko& l : {Laatikko{{1, 0, 1}, {3, 2.5, 3}},
                              Laatikko{{-9, 0, 2}, {-8, 4, 3}}})
        for (const Kolmio& k :
             kolmioiksi(laatikkoverkko(l.min, l.max), yksikko()))
            kolmiot.push_back(k);
    std::vector<Laatikko> laatikot;
    for (const Kolmio& k : kolmiot) laatikot.push_back(ymparys(k));
    Bvh puu = rakenna_bvh(laatikot);
    std::println("{} kolmiota, {} solmua, syvyys {}", kolmiot.size(),
                 puu.solmut.size(), syvyys(puu));
    // @loppu maailma

    // @alku sateet
    struct Tapaus {
        const char* nimi;
        Sade sade;
    };
    const Tapaus tapaukset[] = {
        {"ylhäältä kumpuun", {{-6, 20, -5}, {0, -1, 0}}},
        {"vaakasuoraan laatikkoon", {{-11, 1, 2}, {1, 0, 0}}},
        {"maaston yli ohi", {{-11, 9, 0}, {1, 0, 0}}},
    };
    std::println("\n{:26} {:>9} {:>14} {:>14}", "säde", "etäisyys",
                 "laatikkotestit", "kolmiotestit");
    for (const Tapaus& t : tapaukset) {
        BvhLaskuri laskuri;
        Osuma o = sade_bvh(
            puu, t.sade,
            [&](int i) { return sade_kolmio(t.sade, kolmiot[i]); }, nullptr,
            &laskuri);
        std::println("{:26} {:>9} {:>14} {:>14}", t.nimi,
                     o.osuu ? luku(o.t) : "ei osu", laskuri.solmuja,
                     laskuri.kohteita);
    }
    // @loppu sateet

    // @alku vertailu
    // Kaksisataa sädettä näennäissatunnaisista pisteistä alaviistoon:
    // BVH:n on löydettävä sama osuma kuin kaikkien kolmioiden testauksen.
    unsigned tila = 12345;
    auto satunnainen = [&tila]() {  // tasajakauma välillä [0, 1)
        tila = tila * 1664525u + 1013904223u;
        return (tila >> 8) / 16777216.0;
    };
    long testit = 0;
    int osumia = 0, eroja = 0;
    for (int n = 0; n < 200; ++n) {
        Sade s{{-12 + 24 * satunnainen(), 10, -12 + 24 * satunnainen()},
               normalisoi(Vec3{satunnainen() - 0.5, -1.0,
                               satunnainen() - 0.5})};
        Osuma raaka;
        for (const Kolmio& k : kolmiot) {
            Osuma o = sade_kolmio(s, k);
            if (o.osuu && (!raaka.osuu || o.t < raaka.t)) raaka = o;
        }
        BvhLaskuri laskuri;
        Osuma o = sade_bvh(
            puu, s, [&](int i) { return sade_kolmio(s, kolmiot[i]); },
            nullptr, &laskuri);
        testit += laskuri.solmuja + laskuri.kohteita;
        osumia += o.osuu;
        if (o.osuu != raaka.osuu || std::abs(o.t - raaka.t) > 1e-9) ++eroja;
    }
    std::println("\n200 sädettä: {} osumaa, eroja raakaan hakuun {}", osumia,
                 eroja);
    std::println("testejä sädettä kohden: raaka haku {}, BVH {}",
                 kolmiot.size(), testit / 200);
    // @loppu vertailu

    // @alku alue
    // Hahmon lähiympäristö: vain nämä kolmiot tarvitsevat tarkan testin.
    Laatikko alue{{1.5, 0, -0.5}, {2.5, 2, 1.5}};
    BvhLaskuri laskuri;
    int ehdokkaita = 0;
    kay_lapi(
        puu, [&](const Laatikko& l) { return leikkaavat(l, alue); },
        [&](int i) { ehdokkaita += leikkaavat(laatikot[i], alue); },
        &laskuri);
    std::println("\nalueen kysely: {} ehdokasta, {} laatikkotestiä",
                 ehdokkaita, laskuri.solmuja + laskuri.kohteita);
    // @loppu alue

    if (argc > 1) {
        Kuva kuva(560, 340, {150, 185, 225});
        Piirtaja p(kuva, perspektiivi(1 / std::tan(rad(24)), 560.0 / 340,
                                      0.1, 100) *
                             katse({10, 16, 22}, {0, 0, 0}, {0, 1, 0}));
        piirra_maasto(p, maasto);
        piirra(p, laatikkoverkko({1, 0, 1}, {3, 2.5, 3}), yksikko(),
               {190, 110, 80});
        piirra(p, laatikkoverkko({-9, 0, 2}, {-8, 4, 3}), yksikko(),
               {200, 180, 90});
        // Puun kolmen ylimmän tason laatikot.
        struct Taso {
            int solmu, taso;
        };
        std::vector<Taso> pino{{0, 0}};
        const Vari varit[] = {{230, 30, 30}, {250, 220, 50}, {50, 60, 220}};
        while (!pino.empty()) {
            Taso t = pino.back();
            pino.pop_back();
            const BvhSolmu& s = puu.solmut[t.solmu];
            if (t.taso > 0) piirra_reunat(p, s.laatikko, varit[t.taso - 1]);
            if (s.maara == 0 && t.taso < 3) {
                pino.push_back({s.vasen, t.taso + 1});
                pino.push_back({s.oikea, t.taso + 1});
            }
        }
        kuva.tallenna_ppm(argv[1]);
    }
}
