// Nivelet: rajoitteet, jotka sitovat kaksi kappaletta toisiinsa.
// Ratkaistaan samalla tavalla kuin kosketukset, mutta impulssi saa olla
// kumman tahansa merkkinen.
#pragma once
#include "ratkaisija.hpp"

// @alku nivel
struct Nivel {
    enum class Laji { etaisyys, pallo, sarana };
    Laji laji = Laji::pallo;
    int a = 0, b = 0;
    Vec3 kiinnitys_a, kiinnitys_b;  // kiinnityspisteet kappaleiden
                                    // omissa koordinaatistoissa
    double pituus = 0;              // etäisyysrajoitteen pituus
    Vec3 akseli_a, akseli_b;        // saranan akseli kummassakin
    // Kertyneet impulssit lämmintä käynnistystä varten. Yhden rivin
    // rajoitteesta talletetaan luku, ei vektoria: suunta lasketaan
    // joka askeleella uudelleen.
    Vec3 kertyma;        // pallonivel ja sarana
    double kertyma1 = 0;  // etäisyys
    double kulma1 = 0, kulma2 = 0;
};
inline Vec3 maailmaan(const Kappale& k, Vec3 paikallinen) {
    return k.sijainti + kierra(k.kierto, paikallinen);
}
inline Vec3 paikalliseen(const Kappale& k, Vec3 maailma) {
    return kierra(liitto(k.kierto), maailma - k.sijainti);
}
// @loppu nivel

// @alku tehtaat
// Nivelet luodaan maailman pisteestä: kiinnityspisteet lasketaan
// kappaleiden senhetkisestä asennosta.
inline Nivel pallonivel(const std::vector<Kappale>& k, int a, int b,
                        Vec3 piste) {
    Nivel n;
    n.laji = Nivel::Laji::pallo;
    n.a = a;
    n.b = b;
    n.kiinnitys_a = paikalliseen(k[a], piste);
    n.kiinnitys_b = paikalliseen(k[b], piste);
    return n;
}
inline Nivel sarana(const std::vector<Kappale>& k, int a, int b, Vec3 piste,
                    Vec3 akseli) {
    Nivel n = pallonivel(k, a, b, piste);
    n.laji = Nivel::Laji::sarana;
    n.akseli_a = kierra(liitto(k[a].kierto), akseli);
    n.akseli_b = kierra(liitto(k[b].kierto), akseli);
    return n;
}
inline Nivel etaisyysnivel(const std::vector<Kappale>& k, int a, int b,
                           Vec3 piste_a, Vec3 piste_b) {
    Nivel n;
    n.laji = Nivel::Laji::etaisyys;
    n.a = a;
    n.b = b;
    n.kiinnitys_a = paikalliseen(k[a], piste_a);
    n.kiinnitys_b = paikalliseen(k[b], piste_b);
    n.pituus = pituus(piste_b - piste_a);
    return n;
}
// @loppu tehtaat

// @alku valmistelu
struct NivelValmis {
    Vec3 ra, rb;
    Vec3 virhe;          // pallonivel: kiinnityspisteiden ero
    Mat3 massa;          // pallonivel: 3x3-tehollisen massan käänteinen
    Vec3 suunta;         // etäisyys: yksikkövektori a:sta b:hen
    double massa1 = 0, tavoite1 = 0;      // etäisyys
    Vec3 m1, m2;         // sarana: kiertoakselit, joiden ympäri
    double km1 = 0, km2 = 0, t1 = 0, t2 = 0;  // kappaleet eivät saa kiertyä
};
inline NivelValmis valmistele(const std::vector<Kappale>& kappaleet,
                              const Massat& ms, const Nivel& n,
                              const Asetukset& as) {
    const Kappale& a = kappaleet[n.a];
    const Kappale& b = kappaleet[n.b];
    NivelValmis v;
    v.ra = kierra(a.kierto, n.kiinnitys_a);
    v.rb = kierra(b.kierto, n.kiinnitys_b);
    v.virhe = (b.sijainti + v.rb) - (a.sijainti + v.ra);
    if (n.laji == Nivel::Laji::etaisyys) {
        double d = pituus(v.virhe);
        v.suunta = d > 1e-9 ? (1 / d) * v.virhe : Vec3{0, 1, 0};
        v.massa1 = tehollinen_massa(ms, n.a, v.ra, n.b, v.rb, v.suunta);
        v.tavoite1 = -as.beta / as.dt * (d - n.pituus);
        return v;
    }
    // K = (1/ma + 1/mb) 1 - [ra]x Ia^-1 [ra]x - [rb]x Ib^-1 [rb]x
    Mat3 xa = ristimatriisi(v.ra), xb = ristimatriisi(v.rb);
    Mat3 k = lavistaja({ms.km[n.a] + ms.km[n.b], ms.km[n.a] + ms.km[n.b],
                        ms.km[n.a] + ms.km[n.b]}) +
             xa * ms.ki[n.a] * transpoosi(xa) +
             xb * ms.ki[n.b] * transpoosi(xb);
    v.massa = kaanteinen(k);
    if (n.laji == Nivel::Laji::sarana) {
        // Akselien on pysyttävä samansuuntaisina: b:n akseli ei saa
        // saada komponenttia kahteen a:n akselia vastaan kohtisuoraan
        // suuntaan p ja q.
        Vec3 aa = kierra(a.kierto, n.akseli_a);
        Vec3 ab = kierra(b.kierto, n.akseli_b);
        Vec3 p, q;
        tangentit(aa, p, q);
        v.m1 = risti(p, ab);
        v.m2 = risti(q, ab);
        auto kulmamassa = [&](Vec3 m) {
            double k1 = piste(m, ms.ki[n.a] * m) + piste(m, ms.ki[n.b] * m);
            return k1 > 0 ? 1 / k1 : 0.0;
        };
        v.km1 = kulmamassa(v.m1);
        v.km2 = kulmamassa(v.m2);
        v.t1 = -as.beta / as.dt * piste(p, ab);
        v.t2 = -as.beta / as.dt * piste(q, ab);
    }
    return v;
}
// @loppu valmistelu

// @alku ratkaise
inline void kierra_impulssi(std::vector<Kappale>& kappaleet,
                            const Massat& ms, const Nivel& n, Vec3 m,
                            double impulssi) {
    kappaleet[n.a].kulmanopeus =
        kappaleet[n.a].kulmanopeus + ms.ki[n.a] * (impulssi * m);
    kappaleet[n.b].kulmanopeus =
        kappaleet[n.b].kulmanopeus - ms.ki[n.b] * (impulssi * m);
}
inline void lammita(std::vector<Kappale>& kappaleet, const Massat& ms,
                    const Nivel& n, const NivelValmis& v) {
    Vec3 imp = n.laji == Nivel::Laji::etaisyys ? n.kertyma1 * v.suunta
                                               : n.kertyma;
    tyonna(kappaleet, ms, n.a, -imp, v.ra);
    tyonna(kappaleet, ms, n.b, imp, v.rb);
    if (n.laji == Nivel::Laji::sarana) {
        kierra_impulssi(kappaleet, ms, n, v.m1, n.kulma1);
        kierra_impulssi(kappaleet, ms, n, v.m2, n.kulma2);
    }
}
inline void ratkaise(std::vector<Kappale>& kappaleet, const Massat& ms,
                     Nivel& n, const NivelValmis& v, const Asetukset& as) {
    Kappale& a = kappaleet[n.a];
    Kappale& b = kappaleet[n.b];
    Vec3 nopeus = b.nopeus + risti(b.kulmanopeus, v.rb) - a.nopeus -
                  risti(a.kulmanopeus, v.ra);
    Vec3 imp;
    if (n.laji == Nivel::Laji::etaisyys) {
        // Yksi rivi: pisteiden välinen etäisyys ei saa muuttua.
        double i1 = v.massa1 * (v.tavoite1 - piste(nopeus, v.suunta));
        n.kertyma1 += i1;
        imp = i1 * v.suunta;
    } else {
        // Kolme riviä kerralla: kiinnityspisteillä on sama nopeus.
        imp = v.massa * (-nopeus - (as.beta / as.dt) * v.virhe);
        n.kertyma = n.kertyma + imp;
    }
    tyonna(kappaleet, ms, n.a, -imp, v.ra);
    tyonna(kappaleet, ms, n.b, imp, v.rb);
    if (n.laji == Nivel::Laji::sarana) {
        // Kaksi kulmariviä: suhteellinen kulmanopeus akseleiden m1 ja m2
        // ympäri nollaan. Vapaaksi jää kierto saranan akselin ympäri.
        Vec3 w = a.kulmanopeus - b.kulmanopeus;
        double i1 = v.km1 * (v.t1 - piste(w, v.m1));
        kierra_impulssi(kappaleet, ms, n, v.m1, i1);
        n.kulma1 += i1;
        w = a.kulmanopeus - b.kulmanopeus;
        double i2 = v.km2 * (v.t2 - piste(w, v.m2));
        kierra_impulssi(kappaleet, ms, n, v.m2, i2);
        n.kulma2 += i2;
    }
}
// @loppu ratkaise
