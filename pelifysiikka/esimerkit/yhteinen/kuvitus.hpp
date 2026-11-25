// Kuvitus: maailman kappaleet kuviksi paketin pienellä
// ohjelmistorenderöijällä (piirto.hpp). Ei kuulu fysiikkaan.
#pragma once
#include "maailma.hpp"
#include "piirto.hpp"

#include <format>
#include <string>

inline const Vari VARIT[] = {{190, 110, 80},  {90, 120, 190},
                             {200, 180, 90},  {110, 170, 130},
                             {170, 110, 170}, {110, 170, 200}};
inline const Vari TAIVAS{150, 185, 225};
inline const Vari UNESSA{150, 150, 155};

inline void piirra_nelio(Piirtaja& p, Vec3 a, Vec3 b, Vec3 c, Vec3 d,
                         Vari v) {
    p.kolmio(a, b, c, v);
    p.kolmio(a, c, d, v);
}

// Laatikko mallimatriisin läpi: kuusi sivua vastapäivään ulkoa katsoen.
inline void piirra_laatikko(Piirtaja& p, const Mat4& malli, Vec3 e,
                            Vari v) {
    Vec3 k[8];
    for (int i = 0; i < 8; ++i)
        k[i] = muunna_piste(malli, {i & 1 ? e.x : -e.x, i & 2 ? e.y : -e.y,
                                    i & 4 ? e.z : -e.z});
    piirra_nelio(p, k[4], k[5], k[7], k[6], v);  // +z
    piirra_nelio(p, k[1], k[0], k[2], k[3], v);  // -z
    piirra_nelio(p, k[5], k[1], k[3], k[7], v);  // +x
    piirra_nelio(p, k[0], k[4], k[6], k[2], v);  // -x
    piirra_nelio(p, k[6], k[7], k[3], k[2], v);  // +y
    piirra_nelio(p, k[0], k[1], k[5], k[4], v);  // -y
}

// Pallo leveys- ja pituuspiirien ruudukkona. Joka toinen lohko on
// tummempi, jotta pyöriminen näkyy kuvassa.
inline void piirra_pallo(Piirtaja& p, const Mat4& malli, double sade,
                         Vari v, int lohkot = 12) {
    auto piste_pallolla = [&](int i, int j) {
        double lev = PII * i / lohkot, pit = 2 * PII * j / lohkot;
        return muunna_piste(malli, {sade * std::sin(lev) * std::cos(pit),
                                    sade * std::cos(lev),
                                    -sade * std::sin(lev) * std::sin(pit)});
    };
    for (int i = 0; i < lohkot; ++i)
        for (int j = 0; j < lohkot; ++j)
            piirra_nelio(p, piste_pallolla(i, j), piste_pallolla(i + 1, j),
                         piste_pallolla(i + 1, j + 1),
                         piste_pallolla(i, j + 1),
                         (j / 3) % 2 ? himmenna(v, 0.75) : v);
}

// Ruudutettu lattia tasolla y = korkeus.
inline void piirra_lattia(Piirtaja& p, int ruutuja, double koko,
                          double korkeus = 0) {
    for (int i = -ruutuja; i < ruutuja; ++i)
        for (int j = -ruutuja; j < ruutuja; ++j) {
            Vec3 a{i * koko, korkeus, j * koko};
            Vari v = (i + j) & 1 ? Vari{128, 158, 120} : Vari{140, 170, 132};
            piirra_nelio(p, a, a + Vec3{0, 0, koko},
                         a + Vec3{koko, 0, koko}, a + Vec3{koko, 0, 0}, v);
        }
}

inline void piirra_kappale(Piirtaja& p, const Kappale& k, Vari v) {
    Mat4 malli = mallimatriisi(k.sijainti, k.kierto);
    if (k.muoto.laji == Muoto::Laji::pallo)
        piirra_pallo(p, malli, k.muoto.sade, v);
    else if (k.muoto.laji == Muoto::Laji::laatikko)
        piirra_laatikko(p, malli, k.muoto.puolet, v);
}

// Koko maailma: liikkuvat kappaleet väreissä, liikkumattomat laatikot
// harmaina ja nukkuvat vaaleanharmaina. Nivelet viivoina.
inline void piirra_maailma(Piirtaja& p, const Maailma& m,
                           bool lattia = true) {
    if (lattia) piirra_lattia(p, 10, 1.0);
    for (std::size_t i = 0; i < m.kappaleet.size(); ++i) {
        const Kappale& k = m.kappaleet[i];
        Vari v = !k.liikkuva() ? Vari{120, 120, 130}
                 : k.unessa    ? UNESSA
                               : VARIT[i % 6];
        piirra_kappale(p, k, v);
    }
    for (const Nivel& n : m.nivelet)
        p.viiva(maailmaan(m.kappaleet[n.a], n.kiinnitys_a),
                maailmaan(m.kappaleet[n.b], n.kiinnitys_b), {40, 40, 40},
                true);
}

struct Kamera {
    Vec3 silma{6, 4, 9}, kohde{0, 1.5, 0};
    double fov = 40, suhde = 1.6;
};
inline Mat4 nakyma_projektio(const Kamera& k) {
    return perspektiivi(1 / std::tan(rad(k.fov / 2)), k.suhde, 0.1, 200) *
           katse(k.silma, k.kohde, {0, 1, 0});
}

// Tallentaa maailman kuvaksi nimi-N.ppm.
inline void tallenna_kuva(const Maailma& m, const Kamera& kamera,
                          const std::string& nimi, int numero,
                          int leveys = 400, bool lattia = true) {
    Kuva kuva(leveys, static_cast<int>(leveys / kamera.suhde), TAIVAS);
    Piirtaja p(kuva, nakyma_projektio(kamera));
    piirra_maailma(p, m, lattia);
    kuva.tallenna_ppm(std::format("{}-{}.ppm", nimi, numero));
}
inline void tallenna_kuva_ilman_lattiaa(const Maailma& m,
                                        const Kamera& kamera,
                                        const std::string& nimi,
                                        int numero) {
    tallenna_kuva(m, kamera, nimi, numero, 300, false);
}
