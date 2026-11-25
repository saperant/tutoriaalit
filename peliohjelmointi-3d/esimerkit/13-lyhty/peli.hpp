// Lyhty: pieni kolmannen persoonan peli, joka yhdistää tutoriaalin osat.
// Taso ja hahmo ladataan glTF-tiedostoista, hahmo liikkuu kapselina
// kolmioverkossa, kamera seuraa ja väistää seiniä, animaatio sekoittuu
// nopeuden mukaan ja piirtolista karsitaan näkymäkartiolla.
#pragma once
#include "../yhteinen/gltf.hpp"
#include "../yhteinen/hahmo.hpp"
#include "../yhteinen/kartio.hpp"

#include <string>
#include <vector>

// @alku tila
struct Kappale {  // piirrettävä tason osa
    std::string nimi;
    const Verkko* verkko;
    Mat4 malli;
    Vari vari;
    Laatikko ymparys;  // maailmassa, näkyvyyskarsintaa varten
};
struct Lyhty {
    std::string nimi;
    Vec3 paikka;
    bool keratty = false;
};
struct Syote {  // yhden askeleen syöte kameran suhteen
    double eteen = 0, sivulle = 0;  // -1..1
    double kameran_kaanto = 0;      // astetta sekunnissa
    bool hyppy = false;
};
struct Peli {
    Gltf taso, malli;  // ladatut resurssit
    Animoitu animoitu;
    Maailma maailma;
    std::vector<Kappale> kappaleet;
    std::vector<Lyhty> lyhdyt;

    Hahmo hahmo;
    double hahmon_kaanto = 0;   // hahmon suunta, radiaaneina
    double kavelypaino = 0;     // 0 = lepo, 1 = kävely
    double animaatioaika = 0;
    double kameran_kaanto = 0, kameran_etaisyys = 5;
    Vec3 silma;                 // kameran pehmennetty paikka
    double aika = 0;
    int nakyvia = 0;            // viimeksi piirtolistaan päässeet kappaleet
};
// @loppu tila

inline constexpr double DT = 1.0 / 60;

// @alku lataa
inline std::expected<Peli, std::string> lataa_peli() {
    Peli p;
    auto taso = lataa_gltf(resurssi("taso.gltf"));
    if (!taso) return std::unexpected("taso.gltf: " + taso.error());
    auto malli = lataa_gltf(resurssi("hahmo.gltf"));
    if (!malli) return std::unexpected("hahmo.gltf: " + malli.error());
    p.taso = std::move(*taso);
    p.malli = std::move(*malli);
    auto animoitu = luurangoksi(p.malli, 0);
    if (!animoitu) return std::unexpected(animoitu.error());
    p.animoitu = std::move(*animoitu);

    // Solmut, joilla on verkko, ovat sekä näkyvää että törmäävää
    // maailmaa. Tyhjät solmut ovat merkkejä, jotka tunnistetaan nimestä.
    std::vector<Mat4> maailmat = maailmamatriisit(p.taso);
    for (std::size_t i = 0; i < p.taso.solmut.size(); ++i) {
        const GltfSolmu& s = p.taso.solmut[i];
        Vec3 paikka = muunna_piste(maailmat[i], {0, 0, 0});
        if (s.verkko >= 0) {
            const GltfVerkko& v = p.taso.verkot[s.verkko];
            std::vector<Kolmio> kolmiot = kolmioiksi(v.verkko, maailmat[i]);
            Laatikko y = ymparys(kolmiot[0]);
            for (const Kolmio& k : kolmiot) y = yhdiste(y, ymparys(k));
            p.kappaleet.push_back(
                {s.nimi, &v.verkko, maailmat[i], v.vari, y});
            p.maailma.lisaa(v.verkko, maailmat[i]);
        } else if (s.nimi == "alku") {
            p.hahmo.jalat = paikka;
        } else if (s.nimi.starts_with("lyhty.")) {
            p.lyhdyt.push_back({s.nimi, paikka + Vec3{0, 0.8, 0}});
        }
    }
    p.maailma.valmis();
    p.silma = p.hahmo.jalat + Vec3{0, 3, 5};
    return p;
}
// @loppu lataa

// @alku liike
// Syöte tulkitaan kameran suhteen: eteen on kameran katselusuunta
// maan tasossa, sivulle sen oikea puoli.
inline Vec3 liikesuunta(const Peli& p, const Syote& s) {
    Kvat k = akselikulma({0, 1, 0}, p.kameran_kaanto);
    Vec3 suunta = s.eteen * kierra(k, {0, 0, -1}) +
                  s.sivulle * kierra(k, {1, 0, 0});
    return pituus(suunta) > 1 ? normalisoi(suunta) : suunta;
}
// @loppu liike

// @alku kamera
inline Vec3 kameran_kohde(const Peli& p) {
    return p.hahmo.jalat + Vec3{0, 1.5, 0};
}
inline void paivita_kamera(Peli& p) {
    Vec3 kohde = kameran_kohde(p);
    Vec3 taakse = kierra(eulerista(p.kameran_kaanto, rad(-20), 0), {0, 0, 1});
    // Seinä kohteen ja kameran välissä lyhentää etäisyyttä heti;
    // takaisin pidemmäksi palataan pehmeästi.
    Osuma o = p.maailma.sade({kohde, taakse});
    double sallittu = 5;
    if (o.osuu) sallittu = std::clamp(o.t - 0.3, 0.8, 5.0);
    p.kameran_etaisyys =
        sallittu < p.kameran_etaisyys
            ? sallittu
            : sallittu + std::exp(-4 * DT) * (p.kameran_etaisyys - sallittu);
    Vec3 tavoite = kohde + p.kameran_etaisyys * taakse;
    p.silma = tavoite + std::exp(-10 * DT) * (p.silma - tavoite);
}
inline Mat4 nakyma_projektio(const Peli& p, double suhde) {
    return perspektiivi(1 / std::tan(rad(30)), suhde, 0.1, 60) *
           katse(p.silma, kameran_kohde(p), {0, 1, 0});
}
// @loppu kamera

// @alku paivita
// Yksi kiinteä askel. Palauttaa kerätyn lyhdyn nimen tai tyhjän.
inline std::string paivita(Peli& p, const Syote& s) {
    p.kameran_kaanto += rad(s.kameran_kaanto) * DT;
    Vec3 suunta = liikesuunta(p, s);
    askel(p.hahmo, p.maailma, suunta, s.hyppy, DT);

    // Hahmo kääntyy liikesuuntaansa ja animaatio seuraa nopeutta.
    bool liikkuu = pituus(suunta) > 0.1;
    if (liikkuu) {
        // Hahmon nenä on +z-suunnassa (glTF:n sopimus).
        double tavoite = std::atan2(suunta.x, suunta.z);
        double ero = std::remainder(tavoite - p.hahmon_kaanto, 2 * PII);
        p.hahmon_kaanto += (1 - std::exp(-12 * DT)) * ero;
    }
    double tavoitepaino = liikkuu ? 1 : 0;
    p.kavelypaino = tavoitepaino +
                    std::exp(-8 * DT) * (p.kavelypaino - tavoitepaino);
    p.animaatioaika += DT;
    paivita_kamera(p);
    p.aika += DT;

    // Lyhty kerätään, kun hahmon kapseli koskee sen laukaisupalloa.
    for (Lyhty& l : p.lyhdyt) {
        Pallo laukaisin{l.paikka, 0.6};
        if (!l.keratty && tormaa(p.hahmo.kapseli(), laukaisin).osuu) {
            l.keratty = true;
            return l.nimi;
        }
    }
    return "";
}
// @loppu paivita

// @alku poosi
inline Poosi hahmon_poosi(const Peli& p) {
    const Luuranko& l = p.animoitu.luuranko;
    return sekoita(nayte(p.animoitu.leikkeet[0], l, p.animaatioaika),
                   nayte(p.animoitu.leikkeet[1], l, p.animaatioaika),
                   p.kavelypaino);
}
// @loppu poosi

// @alku piirtolista
// Piirtolista: vain kappaleet, joiden ympärys osuu näkymäkartioon.
inline std::vector<const Kappale*> piirtolista(Peli& p, double suhde) {
    auto tasot = kartion_tasot(nakyma_projektio(p, suhde));
    std::vector<const Kappale*> lista;
    for (const Kappale& k : p.kappaleet)
        if (nakyy(tasot, k.ymparys)) lista.push_back(&k);
    p.nakyvia = static_cast<int>(lista.size());
    return lista;
}
// @loppu piirtolista

// Piirtää ruudun: taso, lyhdyt ja skinnattu hahmo.
inline void piirra_ruutu(Peli& p, Kuva& kuva) {
    double suhde = static_cast<double>(kuva.leveys()) / kuva.korkeus();
    Piirtaja piirtaja(kuva, nakyma_projektio(p, suhde));
    for (const Kappale* k : piirtolista(p, suhde))
        piirra(piirtaja, *k->verkko, k->malli, k->vari);
    for (const Lyhty& l : p.lyhdyt)
        if (!l.keratty)
            piirra(piirtaja, palloverkko(0.25, 8), siirto(l.paikka),
                   {250, 220, 70});
    const GltfVerkko& v = p.malli.verkot[0];
    std::vector<Mat4> skin =
        skinnausmatriisit(p.animoitu.luuranko, hahmon_poosi(p));
    Mat4 malli = siirto(p.hahmo.jalat) *
                 matriisiksi(akselikulma({0, 1, 0}, p.hahmon_kaanto));
    Verkko poosissa = v.verkko;
    for (std::size_t i = 0; i < poosissa.pisteet.size(); ++i)
        poosissa.pisteet[i] = skinnaa(v.verkko.pisteet[i], v.painot[i], skin);
    piirra(piirtaja, poosissa, malli, v.vari);
}
