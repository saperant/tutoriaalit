// Törmäysvaste yhdessä kosketuspisteessä, kun kappaleet saavat pyöriä:
// impulssin kaava, säilyvät suureet ja kimmokertoimen vaikutus.
// Argumenttina annettuun nimeen tallennetaan kuvasarja.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku impulssi
// Kappaleet a ja b koskettavat pisteessä p, normaali n osoittaa a:sta
// b:hen. Impulssi j n muuttaa kosketuspisteiden suhteellisen
// normaalinopeuden arvoon -e * (nopeus ennen törmäystä).
double tormaysimpulssi(Kappale& a, Kappale& b, Vec3 p, Vec3 n, double e) {
    Vec3 ra = p - a.sijainti, rb = p - b.sijainti;
    double vn = piste(pisteen_nopeus(b, p) - pisteen_nopeus(a, p), n);
    if (vn >= 0) return 0;  // kappaleet erkanevat jo
    // Nimittäjä: kuinka paljon yksikköimpulssi muuttaa nopeuseroa.
    // Pyöriminen tekee kosketuspisteestä "kevyemmän" kuin koko kappale.
    double k = a.kaanteismassa + b.kaanteismassa +
               piste(n, risti(kaanteishitaus(a) * risti(ra, n), ra)) +
               piste(n, risti(kaanteishitaus(b) * risti(rb, n), rb));
    double j = -(1 + e) * vn / k;
    anna_impulssi(a, -j * n, p);
    anna_impulssi(b, j * n, p);
    return j;
}
// @loppu impulssi

// @alku tilanne
// Pallo osuu avaruudessa leijuvan lankun päähän. Painovoimaa ei ole.
struct Tilanne {
    Kappale pallo = tee_pallo(1.0, 0.2, {0.8, 0, 1.0});
    Kappale lankku = tee_laatikko(4.0, {1.0, 0.1, 0.25}, {});
    Tilanne() { pallo.nopeus = {0, 0, -3}; }
};
Vec3 liikemaara_yht(const Tilanne& t) {
    return liikemaara(t.pallo) + liikemaara(t.lankku);
}
Vec3 momentti_yht(const Tilanne& t) {
    return liikemaaramomentti(t.pallo) + liikemaaramomentti(t.lankku);
}
double energia_yht(const Tilanne& t) {
    return liike_energia(t.pallo) + liike_energia(t.lankku);
}
// @loppu tilanne

int main(int argc, char** argv) {
    // @alku vertailu
    for (double e : {1.0, 0.5, 0.0}) {
        Tilanne t;
        Vec3 p0 = liikemaara_yht(t), l0 = momentti_yht(t);
        double e0 = energia_yht(t);
        Vec3 kohta{0.8, 0, 0.25};  // lankun kylki pallon kohdalla
        double j = tormaysimpulssi(t.lankku, t.pallo, kohta, {0, 0, 1}, e);
        std::println("e = {}: impulssi {} N s", luku(e, 1), luku(j, 3));
        std::println("  pallo  v {}", teksti(t.pallo.nopeus));
        std::println("  lankku v {}  w {}", teksti(t.lankku.nopeus),
                     teksti(t.lankku.kulmanopeus));
        std::println("  liikemäärä {} -> {}", teksti(p0),
                     teksti(liikemaara_yht(t)));
        std::println("  liikemäärämomentti {} -> {}", teksti(l0),
                     teksti(momentti_yht(t)));
        std::println("  liike-energia {} -> {} J", luku(e0, 3),
                     luku(energia_yht(t), 3));
    }
    // @loppu vertailu

    // @alku pudotus
    // Vaakasuora lankku putoaa niin, että vain toinen pää osuu
    // pöydän reunaan. Osuma pysäyttää pään ja panee lankun pyörimään.
    Kappale lankku = tee_laatikko(4.0, {1.0, 0.1, 0.25}, {0, 1, 0});
    lankku.nopeus = {0, -3, 0};
    Kappale poyta = tee_seina({1, 1, 1}, {1.9, -0.1, 0});
    Vec3 kohta{0.9, 0.9, 0};
    // Liikemäärämomentti osumakohdan suhteen ei muutu, koska impulssin
    // varsi siihen on nolla.
    auto momentti = [&] {
        return liikemaaramomentti(lankku) -
               risti(kohta, liikemaara(lankku));
    };
    Vec3 ennen = momentti();
    tormaysimpulssi(poyta, lankku, kohta, {0, 1, 0}, 0.0);
    std::println("\nlankun pää osuu pöytään:");
    std::println("  massakeskipiste v {}  w {}", teksti(lankku.nopeus),
                 teksti(lankku.kulmanopeus));
    std::println("  osuneen pään nopeus {}",
                 teksti(pisteen_nopeus(lankku, kohta)));
    std::println("  vapaan pään nopeus  {}",
                 teksti(pisteen_nopeus(lankku, {-1, 0.9, 0})));
    std::println("  momentti osumakohdan suhteen {} -> {}", teksti(ennen),
                 teksti(momentti()));
    // @loppu pudotus

    if (argc > 1) {  // kuvasarja: pallo osuu lankkuun, e = 0,5
        Maailma m;
        m.asetukset.painovoima = {};
        Tilanne t;
        m.lisaa(t.lankku);
        m.lisaa(t.pallo);
        m.kappaleet[0].kimmoisuus = m.kappaleet[1].kimmoisuus = 0.5;
        Kamera kamera{{0, 5.5, 0.01}, {0, 0, 0}, 40, 1.4};
        int kuvia = 0;
        for (int i = 0; i <= 90; ++i) {
            if (i % 30 == 0)
                tallenna_kuva_ilman_lattiaa(m, kamera, argv[1], ++kuvia);
            m.askel();
        }
    }
}
