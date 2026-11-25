// Fysiikkamaailma: kappaleet, nivelet ja simulaatioaskel.
#pragma once
#include "nivel.hpp"

#include <numeric>

// @alku laaja
// Laaja vaihe: akselien suuntaiset ympärykset järjestetään x-akselin
// mukaan ja pyyhkäistään (sort and sweep). Vain parit, joiden
// ympärykset leikkaavat, pääsevät kapeaan vaiheeseen.
struct Ymparys {
    Vec3 min, max;
};
inline Ymparys ymparys(const Kappale& k) {
    Vec3 e{k.muoto.sade, k.muoto.sade, k.muoto.sade};
    if (k.muoto.laji == Muoto::Laji::laatikko) {
        Akselit ak = akselit(k);
        Vec3 p = k.muoto.puolet;
        e = {};
        for (int i = 0; i < 3; ++i) {
            double puoli = komponentti(p, i);
            e = e + Vec3{puoli * std::abs(ak.u[i].x),
                         puoli * std::abs(ak.u[i].y),
                         puoli * std::abs(ak.u[i].z)};
        }
    }
    // Kosketusmarginaalin verran väljä: lähes koskettavat kappaleet
    // pääsevät kapeaan vaiheeseen, joka luo niille ennakoivan
    // kosketuksen.
    Vec3 vali{MARGINAALI, MARGINAALI, MARGINAALI};
    return {k.sijainti - e - vali, k.sijainti + e + vali};
}
inline std::vector<std::pair<int, int>> laaja_vaihe(
    const std::vector<Kappale>& kappaleet) {
    std::vector<std::pair<int, int>> parit;
    std::vector<int> jarjestys, tasot;
    std::vector<Ymparys> y(kappaleet.size());
    for (int i = 0; i < static_cast<int>(kappaleet.size()); ++i) {
        if (kappaleet[i].muoto.laji == Muoto::Laji::taso) {
            tasot.push_back(i);  // ääretön: pariksi kaikille
            continue;
        }
        y[i] = ymparys(kappaleet[i]);
        jarjestys.push_back(i);
    }
    // Vakaa järjestys: tasatilanteessa pienempi indeksi ensin, jotta
    // parien järjestys on sama jokaisella ajokerralla.
    std::stable_sort(jarjestys.begin(), jarjestys.end(),
                     [&](int a, int b) { return y[a].min.x < y[b].min.x; });
    auto kelpaa = [&](int a, int b) {  // ainakin toinen liikkuu
        const Kappale& ka = kappaleet[a];
        const Kappale& kb = kappaleet[b];
        return (ka.liikkuva() && !ka.unessa) ||
               (kb.liikkuva() && !kb.unessa);
    };
    for (int t : tasot)
        for (int i : jarjestys)
            if (kelpaa(t, i)) parit.push_back({t, i});
    for (std::size_t i = 0; i < jarjestys.size(); ++i) {
        int a = jarjestys[i];
        for (std::size_t j = i + 1; j < jarjestys.size(); ++j) {
            int b = jarjestys[j];
            if (y[b].min.x > y[a].max.x) break;  // loput ovat kauempana
            if (y[a].min.y > y[b].max.y || y[b].min.y > y[a].max.y ||
                y[a].min.z > y[b].max.z || y[b].min.z > y[a].max.z)
                continue;
            if (kelpaa(a, b)) parit.push_back({std::min(a, b),
                                               std::max(a, b)});
        }
    }
    std::sort(parit.begin(), parit.end());
    return parit;
}
// @loppu laaja

// @alku pyyhkaisy
// Jatkuva törmäystunnistus pallolle: milloin askeleen aikana (0..1)
// pallo osuu liikkumattomaan esteeseen, kun se siirtyy matkan d?
// Laatikko käsitellään säteen verran paisutettuna, jolloin pallosta
// tulee piste ja testi on säde vastaan laatikko.
inline double osuma_aika(const Kappale& pallo, Vec3 d, const Kappale& este) {
    double r = pallo.muoto.sade;
    if (este.muoto.laji == Muoto::Laji::taso) {
        Vec3 n = tason_normaali(este);
        double korkeus = piste(pallo.sijainti - este.sijainti, n) - r;
        double lahestyy = -piste(d, n);
        if (korkeus < 0 || lahestyy <= korkeus) return 1.0;
        return korkeus / lahestyy;
    }
    if (este.muoto.laji != Muoto::Laji::laatikko) return 1.0;
    Akselit ak = akselit(este);
    Vec3 o = pallo.sijainti - este.sijainti;
    double alku = 0, loppu = 1;
    for (int i = 0; i < 3; ++i) {  // laatat laatikon koordinaatistossa
        double p = piste(o, ak.u[i]), v = piste(d, ak.u[i]);
        double e = komponentti(este.muoto.puolet, i) + r;
        if (std::abs(v) < 1e-12) {
            if (std::abs(p) > e) return 1.0;
            continue;
        }
        double t0 = (-e - p) / v, t1 = (e - p) / v;
        if (t0 > t1) std::swap(t0, t1);
        alku = std::max(alku, t0);
        loppu = std::min(loppu, t1);
        if (alku > loppu) return 1.0;
    }
    // Jo esteessä kiinni oleva tai sitä hipaiseva pallo jätetään
    // tavallisen kosketuksen hoidettavaksi; muuten esteestä poispäin
    // kimpoava pallo jäisi siihen jumiin.
    if (alku <= 0 || loppu - alku < 1e-9) return 1.0;
    return alku;
}
// @loppu pyyhkaisy

// @alku maailma
struct Tilasto {
    int parit = 0;      // laajan vaiheen läpäisseet parit
    int monistot = 0;   // koskettavat parit
    int pisteet = 0;    // kosketuspisteet
    int hereilla = 0;   // liikkuvat kappaleet, jotka eivät nuku
};
// Maailma on pelkkää dataa: sen kopio on täydellinen tilannevedos.
struct Maailma {
    Asetukset asetukset;
    std::vector<Kappale> kappaleet;
    std::vector<Nivel> nivelet;
    std::vector<Monisto> monistot;  // edellisen askeleen kosketukset
    Tilasto tilasto;
    int askelia = 0;

    int lisaa(const Kappale& k) {
        kappaleet.push_back(k);
        return static_cast<int>(kappaleet.size()) - 1;
    }
    void askel();
    void paivita_lepo();
};
// @loppu maailma

// @alku askel
inline void Maailma::askel() {
    const Asetukset& as = asetukset;
    // 1. Voimat nopeuksiksi.
    for (Kappale& k : kappaleet)
        if (!k.unessa) integroi_nopeus(k, as.painovoima, as.dt);

    // 2. Laaja ja kapea vaihe: uudet monistot.
    std::vector<Monisto> uudet;
    auto parit = laaja_vaihe(kappaleet);
    tilasto = {};
    tilasto.parit = static_cast<int>(parit.size());
    for (auto [a, b] : parit) {
        // Nivelellä yhdistetyt kappaleet eivät törmää toisiinsa: nivel
        // jo määrää niiden keskinäisen liikkeen, ja kosketus kiinnitys-
        // kohdan vieressä vain taistelisi sitä vastaan.
        bool nivelessa = false;
        for (const Nivel& n : nivelet)
            if ((n.a == a && n.b == b) || (n.a == b && n.b == a))
                nivelessa = true;
        if (nivelessa) continue;
        Monisto m = kosketa(kappaleet, a, b);
        if (m.pisteet.empty()) continue;
        if (as.lammin) periyta(m, monistot);
        // Liikkuva kappale herättää nukkuvan, johon se osuu.
        for (auto [oma, toinen] : {std::pair{a, b}, std::pair{b, a}})
            if (kappaleet[oma].unessa && kappaleet[toinen].liikkuva() &&
                !kappaleet[toinen].unessa &&
                pituus(kappaleet[toinen].nopeus) > 0.3) {
                kappaleet[oma].unessa = false;
                kappaleet[oma].lepoaika = 0;
            }
        tilasto.pisteet += static_cast<int>(m.pisteet.size());
        uudet.push_back(std::move(m));
    }
    monistot = std::move(uudet);
    tilasto.monistot = static_cast<int>(monistot.size());

    // 3. Rajoitteiden valmistelu ja lämmin käynnistys.
    Massat massat = laske_massat(kappaleet);
    std::vector<Valmisteltu> kv;
    for (const Monisto& m : monistot) {
        kv.push_back(valmistele(kappaleet, massat, m, as));
        lammita(kappaleet, massat, m, kv.back());
    }
    std::vector<NivelValmis> nv;
    for (Nivel& n : nivelet) {
        nv.push_back(valmistele(kappaleet, massat, n, as));
        if (as.lammin) {
            lammita(kappaleet, massat, n, nv.back());
        } else {
            n.kertyma = {};
            n.kertyma1 = n.kulma1 = n.kulma2 = 0;
        }
    }

    // 4. Ratkaisijan kierrokset: nivelet ensin, kosketukset viimeisenä,
    //    koska viimeisenä ratkaistu rajoite toteutuu tarkimmin.
    for (int kierros = 0; kierros < as.kierrokset; ++kierros) {
        for (std::size_t i = 0; i < nivelet.size(); ++i)
            ratkaise(kappaleet, massat, nivelet[i], nv[i], as);
        for (std::size_t i = 0; i < monistot.size(); ++i)
            ratkaise(kappaleet, massat, monistot[i], kv[i]);
    }

    // 5. Paikat ja asennot uusilla nopeuksilla. Nopea kappale siirtyy
    //    enintään ensimmäiseen osumaansa asti.
    for (Kappale& k : kappaleet) {
        if (!k.liikkuva() || k.unessa) continue;
        double osa = 1.0;
        if (k.nopea && k.muoto.laji == Muoto::Laji::pallo)
            for (const Kappale& este : kappaleet)
                if (!este.liikkuva())
                    osa = std::min(osa,
                                   osuma_aika(k, as.dt * k.nopeus, este));
        integroi_paikka(k, osa * as.dt);
    }
    if (as.nukahtaminen) paivita_lepo();
    for (const Kappale& k : kappaleet)
        if (k.liikkuva() && !k.unessa) ++tilasto.hereilla;
    ++askelia;
}
// @loppu askel

// @alku lepo
// Lepotila saarittain: saari on joukko kappaleita, jotka koskettavat
// toisiaan tai ovat nivelellä kiinni. Saari nukahtaa vasta, kun sen
// jokainen kappale on ollut lähes paikallaan puoli sekuntia.
inline void Maailma::paivita_lepo() {
    const double nopeusraja = 0.08, kulmaraja = 0.15, aikaraja = 0.5;
    std::vector<int> juuri(kappaleet.size());
    std::iota(juuri.begin(), juuri.end(), 0);
    auto etsi = [&](int i) {
        while (juuri[i] != i) i = juuri[i] = juuri[juuri[i]];
        return i;
    };
    auto yhdista = [&](int a, int b) {
        // Liikkumaton kappale ei yhdistä saaria: lattia ei tee koko
        // maailmasta yhtä saarta.
        if (!kappaleet[a].liikkuva() || !kappaleet[b].liikkuva()) return;
        a = etsi(a);
        b = etsi(b);
        if (a != b) juuri[std::max(a, b)] = std::min(a, b);
    };
    for (const Monisto& m : monistot) yhdista(m.a, m.b);
    for (const Nivel& n : nivelet) yhdista(n.a, n.b);

    std::vector<double> lyhin(kappaleet.size(), 1e30);
    for (std::size_t i = 0; i < kappaleet.size(); ++i) {
        Kappale& k = kappaleet[i];
        if (!k.liikkuva()) continue;
        bool levossa = pituus(k.nopeus) < nopeusraja &&
                       pituus(k.kulmanopeus) < kulmaraja;
        k.lepoaika = levossa ? k.lepoaika + asetukset.dt : 0;
        int s = etsi(static_cast<int>(i));
        lyhin[s] = std::min(lyhin[s], k.lepoaika);
    }
    for (std::size_t i = 0; i < kappaleet.size(); ++i) {
        Kappale& k = kappaleet[i];
        if (!k.liikkuva()) continue;
        bool nukkuu = lyhin[etsi(static_cast<int>(i))] > aikaraja;
        if (nukkuu && !k.unessa) k.nopeus = k.kulmanopeus = {};
        k.unessa = nukkuu;
    }
}
// @loppu lepo

// @alku energia
// Koko maailman mekaaninen energia: liike-energia ja potentiaalienergia
// painovoimakentässä.
inline double energia(const Maailma& m) {
    double e = 0;
    for (const Kappale& k : m.kappaleet)
        if (k.liikkuva())
            e += liike_energia(k) -
                 massa(k) * piste(m.asetukset.painovoima, k.sijainti);
    return e;
}
// @loppu energia
