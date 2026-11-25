// glTF-resurssien lataus: tiedoston sisältö, luuranko ja animaatiot
// sekä rikkinäisen tiedoston käsittely.
#include "yhteinen/gltf.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku yhteenveto
void yhteenveto(const char* nimi, const Gltf& g) {
    std::size_t pisteita = 0, kolmioita = 0;
    for (const GltfVerkko& v : g.verkot) {
        pisteita += v.verkko.pisteet.size();
        kolmioita += v.verkko.kolmiot.size();
    }
    std::println("{}: {} solmua, {} verkkoa ({} verteksiä, {} kolmiota),\n"
                 "  {} ihoa, {} animaatiota",
                 nimi, g.solmut.size(), g.verkot.size(), pisteita, kolmioita,
                 g.ihot.size(), g.animaatiot.size());
}
// @loppu yhteenveto

int main() {
    // @alku lataus
    auto hahmo = lataa_gltf(resurssi("hahmo.gltf"));
    auto taso = lataa_gltf(resurssi("taso.gltf"));
    if (!hahmo || !taso) {
        std::println("lataus epäonnistui: {}",
                     !hahmo ? hahmo.error() : taso.error());
        return 1;
    }
    yhteenveto("hahmo.gltf", *hahmo);
    yhteenveto("taso.gltf", *taso);
    // @loppu lataus

    // @alku instanssit
    // Tasossa sama verkko on monen solmun käytössä eri muunnoksilla.
    std::vector<Mat4> maailmat = maailmamatriisit(*taso);
    std::println("\nTason solmut:");
    for (std::size_t i = 0; i < taso->solmut.size(); ++i) {
        const GltfSolmu& s = taso->solmut[i];
        std::println("  {:10} {:13} paikka {}", s.nimi,
                     s.verkko >= 0 ? taso->verkot[s.verkko].nimi : "(merkki)",
                     teksti(muunna_piste(maailmat[i], {0, 0, 0}), 1));
    }
    // @loppu instanssit

    // @alku luuranko
    auto animoitu = luurangoksi(*hahmo, 0);
    if (!animoitu) {
        std::println("luuranko: {}", animoitu.error());
        return 1;
    }
    const Luuranko& l = animoitu->luuranko;
    std::println("\nHahmon nivelet sidontapoosissa:");
    std::vector<Mat4> nivelet = nivelmatriisit(l, lepopoosi(l));
    for (std::size_t i = 0; i < nivelet.size(); ++i)
        std::println("  {:9} vanhempi {:2}  paikka {}", l.nivelet[i].nimi,
                     l.nivelet[i].vanhempi,
                     teksti(muunna_piste(nivelet[i], {0, 0, 0})));
    // Tiedoston käänteisten sidontamatriisien pitää vastata lepopoosia.
    Luuranko laskettu = l;
    laske_sidonta(laskettu);
    double ero = 0;
    for (std::size_t n = 0; n < l.nivelet.size(); ++n) {
        const Mat4& a = l.nivelet[n].kaanteinen_sidonta;
        const Mat4& b = laskettu.nivelet[n].kaanteinen_sidonta;
        for (int i = 0; i < 4; ++i)
            for (int j = 0; j < 4; ++j)
                ero = std::max(ero, std::abs(a.m[i][j] - b.m[i][j]));
    }
    std::println("sidontamatriisit: suurin ero laskettuun {}", luku(ero, 6));
    // @loppu luuranko

    // @alku kavely
    for (const Leike& leike : animoitu->leikkeet)
        std::println("animaatio {:7} kesto {} s, {} kanavaa", leike.nimi,
                     luku(leike.kesto, 1), leike.kanavat.size());
    const Leike& kavely = animoitu->leikkeet.at(1);
    // Vasemman jalkaterän paikka: piste lonkkanivelen koordinaatistossa.
    std::println("vasen jalkaterä kävelyn aikana:");
    for (double t : {0.0, 0.2, 0.4, 0.6}) {
        std::vector<Mat4> m = nivelmatriisit(l, nayte(kavely, l, t));
        std::println("  t = {}  {}", luku(t, 1),
                     teksti(muunna_piste(m[5], {0, -0.9, 0})));
    }
    // @loppu kavely

    // @alku rikki
    // Rikkinäinen resurssi: kopioidaan kuvaus, mutta binääritiedostosta
    // puuttuu loppu. Lataus palauttaa virheen eikä lue muistin ohi.
    namespace fs = std::filesystem;
    fs::copy_file(resurssi("hahmo.gltf"), "rikki.gltf",
                  fs::copy_options::overwrite_existing);
    {
        std::ifstream koko(resurssi("hahmo.bin"), std::ios::binary);
        std::vector<char> data(1000);
        koko.read(data.data(), 1000);
        std::ofstream("hahmo.bin", std::ios::binary).write(data.data(), 1000);
    }
    auto rikki = lataa_gltf("rikki.gltf");
    std::println("\nrikki.gltf: {}",
                 rikki ? "latautui" : "virhe: " + rikki.error());
    auto puuttuva = lataa_gltf("ei-ole.gltf");
    std::println("ei-ole.gltf: {}",
                 puuttuva ? "latautui" : "virhe: " + puuttuva.error());
    // @loppu rikki
}
