// Kosketusten ratkaisija: peräkkäiset impulssit (sequential impulses)
// kertyvine impulsseineen, kitkoineen ja sijainnin korjauksineen.
#pragma once
#include "kosketus.hpp"

// @alku asetukset
struct Asetukset {
    double dt = 1.0 / 60;
    Vec3 painovoima{0, -9.81, 0};
    int kierrokset = 10;        // ratkaisijan iteraatiot askeleessa
    bool lammin = true;         // lämmin käynnistys edellisestä askeleesta
    double beta = 0.2;          // Baumgarten kerroin: osuus virheestä/askel
    double vara = 0.005;        // sallittu tunkeuma (m), jota ei korjata
    double kimmoraja = 1.0;     // tätä hitaampi osuma ei kimpoa (m/s)
    bool nukahtaminen = false;  // lepotila (luku 9)
};
// @loppu asetukset

// @alku massat
// Ratkaisijan näkemä massa. Liikkumaton tai nukkuva kappale on
// käänteismassa nolla, jolloin impulssit eivät liikuta sitä.
struct Massat {
    std::vector<double> km;  // käänteismassat
    std::vector<Mat3> ki;    // käänteishitaudet maailmassa
};
inline Massat laske_massat(const std::vector<Kappale>& kappaleet) {
    Massat m;
    for (const Kappale& k : kappaleet) {
        bool mukana = k.liikkuva() && !k.unessa;
        m.km.push_back(mukana ? k.kaanteismassa : 0.0);
        m.ki.push_back(mukana ? kaanteishitaus(k) : Mat3{});
    }
    return m;
}
// Impulssi p kappaleen i pisteeseen, jonka paikka massakeskipisteestä
// on r.
inline void tyonna(std::vector<Kappale>& kappaleet, const Massat& m, int i,
                   Vec3 p, Vec3 r) {
    Kappale& k = kappaleet[i];
    k.nopeus = k.nopeus + m.km[i] * p;
    k.kulmanopeus = k.kulmanopeus + m.ki[i] * risti(r, p);
}
// Tehollinen massa: kuinka suuren impulssin suunnassa n tarvitaan, jotta
// kosketuspisteiden suhteellinen nopeus muuttuu yhden yksikön.
inline double tehollinen_massa(const Massat& m, int a, Vec3 ra, int b,
                               Vec3 rb, Vec3 n) {
    double k = m.km[a] + m.km[b] +
               piste(n, risti(m.ki[a] * risti(ra, n), ra)) +
               piste(n, risti(m.ki[b] * risti(rb, n), rb));
    return k > 0 ? 1 / k : 0;
}
// @loppu massat

// @alku tangentit
// Kaksi normaalia vastaan kohtisuoraa yksikkövektoria kitkaa varten.
inline void tangentit(Vec3 n, Vec3& t1, Vec3& t2) {
    Vec3 apu = std::abs(n.x) < 0.57 ? Vec3{1, 0, 0} : Vec3{0, 1, 0};
    t1 = normalisoi(risti(n, apu));
    t2 = risti(n, t1);
}
// @loppu tangentit

// @alku valmistelu
// Askeleen ajan vakiona pysyvät luvut yhdelle kosketuspisteelle.
struct Rivi {
    Vec3 ra, rb;         // kosketuspiste kummankin massakeskipisteestä
    double mn, mt1, mt2;  // teholliset massat
    double tavoite;       // haluttu erkanemisnopeus normaalin suunnassa
};
struct Valmisteltu {
    Vec3 t1, t2;
    double kitka = 0;
    std::vector<Rivi> rivit;
};
inline Vec3 suhteellinen_nopeus(const std::vector<Kappale>& kappaleet,
                                const Monisto& m, const Rivi& r) {
    const Kappale& a = kappaleet[m.a];
    const Kappale& b = kappaleet[m.b];
    return b.nopeus + risti(b.kulmanopeus, r.rb) - a.nopeus -
           risti(a.kulmanopeus, r.ra);
}
inline Valmisteltu valmistele(const std::vector<Kappale>& kappaleet,
                              const Massat& massat, const Monisto& m,
                              const Asetukset& as) {
    const Kappale& a = kappaleet[m.a];
    const Kappale& b = kappaleet[m.b];
    Valmisteltu v;
    tangentit(m.normaali, v.t1, v.t2);
    v.kitka = std::sqrt(a.kitka * b.kitka);
    double e = std::max(a.kimmoisuus, b.kimmoisuus);
    for (const Kosketuspiste& p : m.pisteet) {
        Rivi r;
        r.ra = p.piste - a.sijainti;
        r.rb = p.piste - b.sijainti;
        r.mn = tehollinen_massa(massat, m.a, r.ra, m.b, r.rb, m.normaali);
        r.mt1 = tehollinen_massa(massat, m.a, r.ra, m.b, r.rb, v.t1);
        r.mt2 = tehollinen_massa(massat, m.a, r.ra, m.b, r.rb, v.t2);
        // Baumgarten korjaus: osa tunkeumasta muutetaan nopeudeksi.
        // Jos pintojen välissä on vielä rako, kappaleet saavat lähestyä
        // korkeintaan niin, että rako sulkeutuu tämän askeleen aikana.
        r.tavoite = p.syvyys < 0
                        ? p.syvyys / as.dt
                        : as.beta / as.dt *
                              std::max(0.0, p.syvyys - as.vara);
        // Kimmoisuus: lähestymisnopeus käännetään, jos osuma on kova.
        double vn = piste(suhteellinen_nopeus(kappaleet, m, r), m.normaali);
        if (vn < -as.kimmoraja) r.tavoite = std::max(r.tavoite, -e * vn);
        v.rivit.push_back(r);
    }
    return v;
}
// @loppu valmistelu

// @alku lammita
// Lämmin käynnistys: edellisen askeleen impulssit annetaan heti, jolloin
// iterointi alkaa läheltä ratkaisua.
inline void lammita(std::vector<Kappale>& kappaleet, const Massat& massat,
                    const Monisto& m, const Valmisteltu& v) {
    for (std::size_t i = 0; i < m.pisteet.size(); ++i) {
        const Kosketuspiste& p = m.pisteet[i];
        Vec3 imp = p.jn * m.normaali + p.jt1 * v.t1 + p.jt2 * v.t2;
        tyonna(kappaleet, massat, m.a, -imp, v.rivit[i].ra);
        tyonna(kappaleet, massat, m.b, imp, v.rivit[i].rb);
    }
}
// @loppu lammita

// @alku kitka
// Impulssi imp moniston m riville r: a:lle vastakkainen, b:lle sama.
inline void anna(std::vector<Kappale>& kappaleet, const Massat& massat,
                 const Monisto& m, const Rivi& r, Vec3 imp) {
    tyonna(kappaleet, massat, m.a, -imp, r.ra);
    tyonna(kappaleet, massat, m.b, imp, r.rb);
}
// Kitka: suhteellinen liukumisnopeus kohti nollaa, mutta KERTYNYT
// impulssi enintään kitkakerroin * normaali-impulssi.
inline void ratkaise_kitka(std::vector<Kappale>& kappaleet,
                           const Massat& massat, Monisto& m,
                           const Valmisteltu& v) {
    for (std::size_t i = 0; i < m.pisteet.size(); ++i) {
        Kosketuspiste& p = m.pisteet[i];
        const Rivi& r = v.rivit[i];
        double raja = v.kitka * p.jn;
        Vec3 nopeus = suhteellinen_nopeus(kappaleet, m, r);
        double uusi = std::clamp(p.jt1 - r.mt1 * piste(nopeus, v.t1),
                                 -raja, raja);
        anna(kappaleet, massat, m, r, (uusi - p.jt1) * v.t1);
        p.jt1 = uusi;
        nopeus = suhteellinen_nopeus(kappaleet, m, r);
        uusi = std::clamp(p.jt2 - r.mt2 * piste(nopeus, v.t2), -raja, raja);
        anna(kappaleet, massat, m, r, (uusi - p.jt2) * v.t2);
        p.jt2 = uusi;
    }
}
// @loppu kitka

// @alku normaali
// Normaali: kappaleet saavat erkautua mutta eivät lähestyä tavoitetta
// nopeammin. Kertynyt impulssi ei saa olla negatiivinen, koska kosketus
// ei vedä.
inline void ratkaise_normaali(std::vector<Kappale>& kappaleet,
                              const Massat& massat, Monisto& m,
                              const Valmisteltu& v) {
    for (std::size_t i = 0; i < m.pisteet.size(); ++i) {
        Kosketuspiste& p = m.pisteet[i];
        const Rivi& r = v.rivit[i];
        Vec3 nopeus = suhteellinen_nopeus(kappaleet, m, r);
        double uusi = std::max(
            0.0, p.jn + r.mn * (r.tavoite - piste(nopeus, m.normaali)));
        anna(kappaleet, massat, m, r, (uusi - p.jn) * m.normaali);
        p.jn = uusi;
    }
}
// @loppu normaali

// @alku ratkaise
// Yksi kierros yhdelle monistolle. Kitka ensin ja normaalit viimeisenä,
// koska tunkeutumisen estäminen on tärkeämpää kuin kitkan tarkkuus.
inline void ratkaise(std::vector<Kappale>& kappaleet, const Massat& massat,
                     Monisto& m, const Valmisteltu& v) {
    ratkaise_kitka(kappaleet, massat, m, v);
    ratkaise_normaali(kappaleet, massat, m, v);
}
// @loppu ratkaise

// @alku periyta
// Uuden moniston pisteet perivät vanhan moniston impulssit, jos piste
// on pysynyt lähes paikallaan.
inline void periyta(Monisto& uusi, const std::vector<Monisto>& vanhat) {
    for (const Monisto& vanha : vanhat) {
        if (vanha.a != uusi.a || vanha.b != uusi.b) continue;
        for (Kosketuspiste& p : uusi.pisteet)
            for (const Kosketuspiste& q : vanha.pisteet)
                if (pituus(p.piste - q.piste) < 0.02) {
                    p.jn = q.jn;
                    p.jt1 = q.jt1;
                    p.jt2 = q.jt2;
                    break;
                }
    }
}
// @loppu periyta
