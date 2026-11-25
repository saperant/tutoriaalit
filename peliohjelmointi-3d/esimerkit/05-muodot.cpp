// Törmäystestit kolmessa ulottuvuudessa: jokainen palautuu lähimmän
// pisteen etsimiseen. Argumenttina annettuun tiedostoon piirretään
// vianetsintäkuva kosketusnormaaleineen.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <vector>

std::vector<Kosketus> kosketukset;

// @alku rivi
void rivi(const char* nimi, const Kosketus& k) {
    if (!k.osuu) {
        std::println("{:20} ei osu", nimi);
        return;
    }
    std::println("{:20} normaali {:21} syvyys {}", nimi,
                 teksti(k.normaali), luku(k.syvyys));
    kosketukset.push_back(k);
}
// @loppu rivi

int main(int argc, char** argv) {
    // @alku muodot
    Pallo pallo{{0, 0.8, 0}, 1.0};
    Pallo pieni{{1.5, 1.2, 0}, 0.8};
    Laatikko laatikko{{-3, 0, -1}, {-0.7, 1.5, 1}};
    Kapseli hahmo{{2.2, 0.3, 1.5}, {2.2, 1.4, 1.5}, 0.4};  // pystyssä
    Kapseli palkki{{1.6, 1.6, 0.5}, {2.6, 1.6, 2.5}, 0.3};  // vaakasuora
    Kolmio lattia{{-5, 0, 5}, {5, 0, 5}, {0, 0, -5}};
    // @loppu muodot

    // @alku lahin
    std::println("Lähin piste lattiakolmiossa:");
    for (Vec3 p : {Vec3{0, 2, 2}, Vec3{0, 2, 7}, Vec3{8, 2, 7}})
        std::println("  pisteelle {:20} {}", teksti(p),
                     teksti(lahin_kolmiossa(p, lattia)));
    // @loppu lahin

    // @alku testit
    std::println("\nTestit:");
    rivi("pallo - pieni pallo", tormaa(pallo, pieni));
    rivi("pallo - laatikko", tormaa(pallo, laatikko));
    rivi("pallo - lattia", tormaa(pallo, lattia));
    rivi("hahmo - lattia", tormaa(hahmo, lattia));
    rivi("hahmo - pieni pallo", tormaa(hahmo, pieni));
    rivi("hahmo - palkki", tormaa(hahmo, palkki));
    // @loppu testit

    if (argc > 1) {
        Kuva kuva(560, 320, {150, 185, 225});
        Piirtaja p(kuva, perspektiivi(1 / std::tan(rad(20)), 1.75, 0.1, 100) *
                             katse({1, 5, 12}, {0.3, 0.9, 0}, {0, 1, 0}));
        p.kolmio(lattia.a, lattia.b, lattia.c, {130, 160, 120});
        piirra(p, palloverkko(pallo.sade, 16), siirto(pallo.keskus),
               {90, 120, 190});
        piirra(p, palloverkko(pieni.sade, 16), siirto(pieni.keskus),
               {110, 170, 200});
        piirra(p, laatikkoverkko(laatikko.min, laatikko.max), yksikko(),
               {190, 110, 80});
        piirra(p, kapseliverkko(hahmo.sade, 1.9), siirto({2.2, -0.1, 1.5}),
               {200, 180, 90});
        Vec3 suunta = normalisoi(palkki.b - palkki.a);
        piirra(p, kapseliverkko(palkki.sade, pituus(palkki.b - palkki.a) +
                                                 2 * palkki.sade),
               siirto(palkki.a - palkki.sade * suunta) *
                   matriisiksi(kierto_suuntaan({0, 1, 0}, suunta)),
               {170, 170, 175});
        for (const Kosketus& k : kosketukset)  // normaalit punaisella
            p.viiva(k.piste, k.piste + 1.2 * k.normaali, {230, 30, 30},
                    true);
        kuva.tallenna_ppm(argv[1]);
    }
}
