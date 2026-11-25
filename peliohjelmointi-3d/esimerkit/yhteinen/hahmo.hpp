// Kinemaattinen hahmo-ohjain: kapseli, joka liikkuu syötteen mukaan,
// työnnetään irti maailmasta, nousee portaat ja pysyy maassa alamäessä.
#pragma once
#include "maailma.hpp"

// @alku hahmo
struct Hahmo {
    Vec3 jalat;        // kapselin alin piste
    double pysty = 0;  // pystynopeus, m/s
    bool maassa = false;
    bool nousee = false;  // viime askel nousi askelman reunaa

    static constexpr double SADE = 0.4, PITUUS = 1.8;
    Kapseli kapseli() const {
        return {jalat + Vec3{0, SADE, 0}, jalat + Vec3{0, PITUUS - SADE, 0},
                SADE};
    }
};
struct Liikeasetukset {
    double nopeus = 4;        // kävelynopeus, m/s
    double painovoima = 20;   // m/s^2
    double hyppy = 7;         // hypyn lähtönopeus, m/s
    double kaveltava = 0.7;   // maan normaalin pienin y: noin 45 astetta
    double porras = 0.35;     // korkein askelma, jonka yli noustaan
    double tartunta = 0.3;    // matka, jolta hahmo vedetään maahan
};
// @loppu hahmo

// @alku syvin
// Syvin kosketus hahmon ja maailman välillä. Vain kapselin ympärystä
// leikkaavat kolmiot testataan tarkasti.
inline Kosketus syvin_kosketus(const Hahmo& h, const Maailma& maailma) {
    Kosketus syvin;
    Kapseli kapseli = h.kapseli();
    maailma.alueella(ymparys(kapseli), [&](const Kolmio& kolmio) {
        Kosketus k = tormaa(kapseli, kolmio);
        if (k.osuu && k.syvyys > syvin.syvyys) syvin = k;
    });
    return syvin;
}
// @loppu syvin

// @alku ratkaise
// Työntää kapselin irti maailmasta. Joka kierroksella puretaan vain
// syvin kosketus: sen jälkeen viereisten kolmioiden reunoihin syntyneet
// näennäiset kosketukset katoavat itsestään. Käveltävä pinta nostaa
// hahmoa suoraan ylös, jotta se ei valu rinnettä alas; seinä ja liian
// jyrkkä rinne työntävät vaakasuunnassa. Palauttaa, osuiko hahmo seinään.
inline bool ratkaise(Hahmo& h, const Maailma& maailma,
                     const Liikeasetukset& a) {
    bool seina = false;
    h.maassa = false;
    for (int kierros = 0; kierros < 8; ++kierros) {
        Kosketus k = syvin_kosketus(h, maailma);
        if (k.syvyys < 1e-6) break;
        Vec3 n = k.normaali;
        double vaaka = std::sqrt(n.x * n.x + n.z * n.z);
        if (n.y >= a.kaveltava) {
            h.jalat.y += k.syvyys / n.y;
            h.maassa = true;
        } else if (n.y < -0.5 || vaaka < 1e-6) {  // katto
            h.jalat = h.jalat + k.syvyys * n;
            h.pysty = std::min(h.pysty, 0.0);
        } else {
            h.jalat = h.jalat +
                      (k.syvyys / (vaaka * vaaka)) * Vec3{n.x, 0, n.z};
            seina = true;
        }
    }
    return seina;
}
// @loppu ratkaise

// @alku alas
// Laskee hahmoa enintään matkan verran ja pysäyttää sen siihen, mihin
// kapseli ensin osuu: laskun jälkeen läpäisyt puretaan vain ylöspäin.
// Palauttaa, pysäyttikö jokin laskun.
inline bool painu_alas(Hahmo& h, const Maailma& maailma, double matka) {
    double alku = h.jalat.y;
    h.jalat.y -= matka;
    for (int kierros = 0; kierros < 8; ++kierros) {
        Kosketus k = syvin_kosketus(h, maailma);
        if (k.syvyys < 1e-6 || k.normaali.y < 0.05) break;
        h.jalat.y += k.syvyys / k.normaali.y;
    }
    return h.jalat.y > alku - matka + 1e-6;
}
// Onko jalkojen alla (tai sivussa vaakasiirron päässä) käveltävää
// pintaa enintään matkan päässä?
inline bool tukea_alla(const Hahmo& h, const Maailma& maailma, double matka,
                       const Liikeasetukset& a, Vec3 sivussa = {}) {
    Osuma o = maailma.sade(
        {h.jalat + sivussa + Vec3{0, Hahmo::SADE, 0}, {0, -1, 0}});
    return o.osuu && o.normaali.y >= a.kaveltava &&
           o.t <= Hahmo::SADE + matka;
}
// @loppu alas

// @alku askel
// Yksi kiinteä aika-askel. suunta on vaakatason liikesuunta, jonka
// pituus on enintään 1.
inline void askel(Hahmo& h, const Maailma& maailma, Vec3 suunta, bool hyppy,
                  double dt, const Liikeasetukset& a = {}) {
    bool oli_maassa = h.maassa;
    if (oli_maassa && hyppy) {
        h.pysty = a.hyppy;
        oli_maassa = false;
    }
    h.pysty = oli_maassa ? 0 : h.pysty - a.painovoima * dt;
    Vec3 vaaka = (a.nopeus * dt) * suunta;

    // 1. Tavallinen liike ja irrotus maailmasta.
    Hahmo uusi = h;
    uusi.jalat = h.jalat + vaaka + Vec3{0, h.pysty * dt, 0};
    uusi.nousee = false;
    bool seina = ratkaise(uusi, maailma, a);

    // 2. Porras: jos seinä pysäytti maassa kulkevan, sama liike tehdään
    //    askelman verran ylempänä ja hahmo lasketaan alas. Tulos
    //    kelpaa, jos hahmo pääsi pidemmälle ja sekä sen alla että
    //    edessä on käveltävää pintaa (jyrkkä rinne ei ole porras).
    if (seina && oli_maassa) {
        Hahmo ylhaalta = h;
        ylhaalta.jalat = h.jalat + vaaka + Vec3{0, a.porras, 0};
        ratkaise(ylhaalta, maailma, a);
        painu_alas(ylhaalta, maailma, a.porras);
        auto matka = [&h](const Hahmo& x) {
            Vec3 d = x.jalat - h.jalat;
            return std::sqrt(d.x * d.x + d.z * d.z);
        };
        Vec3 edessa = Hahmo::SADE * normalisoi(vaaka);
        if (matka(ylhaalta) > matka(uusi) + 1e-4 &&
            tukea_alla(ylhaalta, maailma, a.porras, a) &&
            tukea_alla(ylhaalta, maailma, a.porras, a, edessa)) {
            uusi = ylhaalta;
            uusi.maassa = uusi.nousee = true;
        }
    }

    // 3. Tartunta: maassa kulkenut hahmo pysyy maassa, jos pinta on
    //    lähellä jalkojen alla. Muuten se alkaa pudota.
    if (oli_maassa && !uusi.maassa) {
        Hahmo alas = uusi;
        if (painu_alas(alas, maailma, a.tartunta) &&
            tukea_alla(alas, maailma, a.porras, a)) {
            uusi = alas;
            uusi.maassa = true;
        }
    }
    if (uusi.maassa) uusi.pysty = 0;
    h = uusi;
}
// @loppu askel
