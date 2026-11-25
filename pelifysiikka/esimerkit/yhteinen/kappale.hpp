// Jäykkä kappale: tila, massaominaisuudet ja niistä johdetut suureet.
#pragma once
#include "kvaternio.hpp"

// @alku muoto
// Törmäysmuoto kappaleen omassa koordinaatistossa, keskipiste origossa.
struct Muoto {
    enum class Laji { taso, pallo, laatikko };
    Laji laji = Laji::pallo;
    double sade = 0.5;       // pallo
    Vec3 puolet{0.5, 0.5, 0.5};  // laatikon puolimitat
};
// @loppu muoto

// @alku kappale
struct Kappale {
    // Tila: paikka ja asento sekä niiden muutosnopeudet.
    Vec3 sijainti;      // massakeskipiste maailmassa
    Kvat kierto;        // asento
    Vec3 nopeus;        // massakeskipisteen nopeus
    Vec3 kulmanopeus;   // maailman koordinaatistossa, rad/s

    // Massaominaisuudet. Käänteismassa 0 tarkoittaa liikkumatonta
    // kappaletta: mikään impulssi ei muuta sen nopeutta.
    double kaanteismassa = 0;
    Vec3 hitaus;        // päähitausmomentit kappaleen koordinaatistossa

    Muoto muoto;
    double kimmoisuus = 0.0;  // kimmokerroin e
    double kitka = 0.5;       // kitkakerroin
    Vec3 voima, vaanto;       // askeleen aikana kertyvät, nollataan

    bool nopea = false;       // jatkuva törmäystunnistus (luku 10)
    bool unessa = false;      // lepotila (luku 9)
    double lepoaika = 0;

    bool liikkuva() const { return kaanteismassa > 0; }
};
// @loppu kappale

// @alku tehtaat
// Tasaisen pallon ja laatikon hitausmomentit massakeskipisteen suhteen.
inline Kappale tee_pallo(double massa, double sade, Vec3 sijainti) {
    Kappale k;
    k.sijainti = sijainti;
    k.kaanteismassa = 1.0 / massa;
    double i = 0.4 * massa * sade * sade;  // 2/5 m r^2
    k.hitaus = {i, i, i};
    k.muoto = {Muoto::Laji::pallo, sade, {sade, sade, sade}};
    return k;
}
inline Kappale tee_laatikko(double massa, Vec3 puolet, Vec3 sijainti) {
    Kappale k;
    k.sijainti = sijainti;
    k.kaanteismassa = 1.0 / massa;
    // Sivujen pituudet ovat 2 * puolimitta: I_x = m/12 (ly^2 + lz^2).
    Vec3 n{puolet.x * puolet.x, puolet.y * puolet.y, puolet.z * puolet.z};
    k.hitaus = {massa / 3 * (n.y + n.z), massa / 3 * (n.x + n.z),
                massa / 3 * (n.x + n.y)};
    k.muoto = {Muoto::Laji::laatikko, 0, puolet};
    return k;
}
// Liikkumaton taso sijainnin kautta; normaali on tason paikallinen +y.
inline Kappale tee_taso(Vec3 sijainti = {}, Kvat kierto = {}) {
    Kappale k;
    k.sijainti = sijainti;
    k.kierto = kierto;
    k.muoto.laji = Muoto::Laji::taso;
    return k;
}
// Liikkumaton laatikko: seinä, lattia tai taso, jolla on reunat.
inline Kappale tee_seina(Vec3 puolet, Vec3 sijainti, Kvat kierto = {}) {
    Kappale k;
    k.sijainti = sijainti;
    k.kierto = kierto;
    k.muoto = {Muoto::Laji::laatikko, 0, puolet};
    return k;
}
// @loppu tehtaat

// @alku hitaus
// Hitaustensori maailman koordinaatistossa: I = R I_paikallinen R^T.
// Se muuttuu aina, kun kappale kääntyy.
inline Mat3 hitaus_maailmassa(const Kappale& k) {
    Mat3 r = kiertomatriisi(k.kierto);
    return r * lavistaja(k.hitaus) * transpoosi(r);
}
inline Mat3 kaanteishitaus(const Kappale& k) {
    if (!k.liikkuva()) return {};  // nollamatriisi: ei käänny
    Mat3 r = kiertomatriisi(k.kierto);
    Vec3 i{1 / k.hitaus.x, 1 / k.hitaus.y, 1 / k.hitaus.z};
    return r * lavistaja(i) * transpoosi(r);
}
// @loppu hitaus

// Suunta kappaleen koordinaatistosta maailmaan (ei siirtoa).
inline Vec3 maailmaan_suunta(const Kappale& k, Vec3 paikallinen) {
    return kierra(k.kierto, paikallinen);
}

// @alku piste
// Kappaleeseen kiinnitetyn pisteen nopeus: v + w x r.
inline Vec3 pisteen_nopeus(const Kappale& k, Vec3 p) {
    return k.nopeus + risti(k.kulmanopeus, p - k.sijainti);
}
// Impulssi j maailman pisteeseen p: liikemäärä muuttuu j:n ja
// liikemäärämomentti r x j:n verran.
inline void anna_impulssi(Kappale& k, Vec3 j, Vec3 p) {
    k.nopeus = k.nopeus + k.kaanteismassa * j;
    k.kulmanopeus = k.kulmanopeus +
                    kaanteishitaus(k) * risti(p - k.sijainti, j);
}
// Voima f maailman pisteeseen p kerää myös vääntömomentin r x f.
inline void lisaa_voima(Kappale& k, Vec3 f, Vec3 p) {
    k.voima = k.voima + f;
    k.vaanto = k.vaanto + risti(p - k.sijainti, f);
}
// @loppu piste

// @alku suureet
inline double massa(const Kappale& k) { return 1.0 / k.kaanteismassa; }
inline Vec3 liikemaara(const Kappale& k) { return massa(k) * k.nopeus; }
// Liikemäärämomentti origon suhteen: rataosa r x p ja pyörimisosa I w.
inline Vec3 liikemaaramomentti(const Kappale& k) {
    return risti(k.sijainti, liikemaara(k)) +
           hitaus_maailmassa(k) * k.kulmanopeus;
}
inline double liike_energia(const Kappale& k) {
    return 0.5 * massa(k) * piste(k.nopeus, k.nopeus) +
           0.5 * piste(k.kulmanopeus,
                       hitaus_maailmassa(k) * k.kulmanopeus);
}
// @loppu suureet

// @alku integroi-nopeus
// Puoli-implisiittinen Euler: ensin nopeudet voimista, sitten paikka
// ja asento uusilla nopeuksilla.
inline void integroi_nopeus(Kappale& k, Vec3 painovoima, double dt) {
    if (!k.liikkuva()) return;
    k.nopeus = k.nopeus + dt * (painovoima + k.kaanteismassa * k.voima);
    k.kulmanopeus = k.kulmanopeus + dt * (kaanteishitaus(k) * k.vaanto);
    k.voima = k.vaanto = {};
}
// @loppu integroi-nopeus

// @alku integroi-paikka
// Asennon muuttuessa hitaustensori muuttuu. Liikemäärämomentti L = I w
// pidetään samana askeleen yli, ja kulmanopeus lasketaan siitä uudessa
// asennossa. Asento päivitetään askeleen puolivälin kulmanopeudella
// (keskipistemenetelmä), jolloin myös pyörimisenergia säilyy hyvin.
inline void integroi_paikka(Kappale& k, double dt) {
    if (!k.liikkuva()) return;
    k.sijainti = k.sijainti + dt * k.nopeus;
    Vec3 l = hitaus_maailmassa(k) * k.kulmanopeus;
    Kappale puolivali = k;
    puolivali.kierto = kierra_askel(k.kierto, k.kulmanopeus, dt / 2);
    Vec3 w = kaanteishitaus(puolivali) * l;
    k.kierto = kierra_askel(k.kierto, w, dt);
    k.kulmanopeus = kaanteishitaus(k) * l;
}
// @loppu integroi-paikka
