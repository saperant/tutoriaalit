// Kangas hiukkasruudukkona kahdella tavalla: jouset ja voimat sekä
// sijaintipohjainen dynamiikka (PBD).
#pragma once
#include "vektori.hpp"

#include <algorithm>
#include <vector>

// @alku kangas
struct Hiukkanen {
    Vec3 sijainti, edellinen, nopeus;
    double kaanteismassa = 1;  // 0 = kiinnitetty
};
struct Lanka {  // kahden hiukkasen välinen etäisyysrajoite tai jousi
    int a, b;
    double lepopituus;
};
struct Kangas {
    int n = 0;  // n x n hiukkasta
    std::vector<Hiukkanen> hiukkaset;
    std::vector<Lanka> langat;
};
// Vaakasuora neliö, sivu metrin; langat ruudukon sivuilla ja
// lävistäjillä (lävistäjät estävät ruutuja painumasta kasaan).
inline Kangas tee_kangas(int n, Vec3 kulma, double sivu) {
    Kangas k;
    k.n = n;
    double vali = sivu / (n - 1);
    for (int j = 0; j < n; ++j)
        for (int i = 0; i < n; ++i) {
            Vec3 p = kulma + Vec3{i * vali, 0, j * vali};
            k.hiukkaset.push_back({p, p, {}, 1.0});
        }
    auto lisaa = [&](int a, int b) {
        k.langat.push_back(
            {a, b,
             pituus(k.hiukkaset[a].sijainti - k.hiukkaset[b].sijainti)});
    };
    for (int j = 0; j < n; ++j)
        for (int i = 0; i < n; ++i) {
            int p = j * n + i;
            if (i + 1 < n) lisaa(p, p + 1);
            if (j + 1 < n) lisaa(p, p + n);
            if (i + 1 < n && j + 1 < n) {
                lisaa(p, p + n + 1);
                lisaa(p + 1, p + n);
            }
        }
    return k;
}
// Suurin suhteellinen venymä: 0,1 tarkoittaa 10 % lepopituutta pidempää.
inline double suurin_venyma(const Kangas& k) {
    double suurin = 0;
    for (const Lanka& l : k.langat)
        suurin = std::max(suurin,
                          pituus(k.hiukkaset[l.a].sijainti -
                                 k.hiukkaset[l.b].sijainti) /
                                  l.lepopituus - 1);
    return suurin;
}
// @loppu kangas

// @alku jouset
// Massa-jousimalli: jokainen lanka on jousi, voimat integroidaan
// puoli-implisiittisellä Eulerilla.
inline void askel_jouset(Kangas& k, double jousivakio, double vaimennus,
                         Vec3 painovoima, double dt) {
    std::vector<Vec3> voima(k.hiukkaset.size());
    for (const Lanka& l : k.langat) {
        Hiukkanen& a = k.hiukkaset[l.a];
        Hiukkanen& b = k.hiukkaset[l.b];
        Vec3 d = b.sijainti - a.sijainti;
        double p = pituus(d);
        Vec3 suunta = (1 / p) * d;
        double f = jousivakio * (p - l.lepopituus) +
                   vaimennus * piste(b.nopeus - a.nopeus, suunta);
        voima[l.a] = voima[l.a] + f * suunta;
        voima[l.b] = voima[l.b] - f * suunta;
    }
    for (std::size_t i = 0; i < k.hiukkaset.size(); ++i) {
        Hiukkanen& h = k.hiukkaset[i];
        if (h.kaanteismassa == 0) continue;
        h.nopeus = h.nopeus + dt * (painovoima + h.kaanteismassa * voima[i]);
        h.sijainti = h.sijainti + dt * h.nopeus;
    }
}
// @loppu jouset

// @alku pbd
// Sijaintipohjainen dynamiikka: 1) ennusta paikat nopeuksista,
// 2) siirrä hiukkasia, kunnes rajoitteet toteutuvat, 3) laske nopeus
// siitä, mihin hiukkanen lopulta päätyi.
inline void askel_pbd(Kangas& k, int kierrokset, Vec3 painovoima, double dt,
                      Vec3 pallon_keskus = {}, double pallon_sade = 0) {
    for (Hiukkanen& h : k.hiukkaset) {
        h.edellinen = h.sijainti;
        if (h.kaanteismassa == 0) continue;
        h.nopeus = h.nopeus + dt * painovoima;
        h.sijainti = h.sijainti + dt * h.nopeus;
    }
    for (int kierros = 0; kierros < kierrokset; ++kierros) {
        for (const Lanka& l : k.langat) {
            Hiukkanen& a = k.hiukkaset[l.a];
            Hiukkanen& b = k.hiukkaset[l.b];
            double w = a.kaanteismassa + b.kaanteismassa;
            if (w == 0) continue;
            Vec3 d = b.sijainti - a.sijainti;
            double p = pituus(d);
            // Virhe jaetaan käänteismassojen suhteessa: kevyt liikkuu
            // enemmän, kiinnitetty ei lainkaan.
            Vec3 korjaus = ((p - l.lepopituus) / (p * w)) * d;
            a.sijainti = a.sijainti + a.kaanteismassa * korjaus;
            b.sijainti = b.sijainti - b.kaanteismassa * korjaus;
        }
        // Törmäys palloon on samanlainen rajoite: hiukkanen ei saa
        // olla pallon sisällä. Kitka: pintaa koskettava hiukkanen
        // palautetaan osittain kohti askeleen alkupaikkaansa.
        if (pallon_sade > 0)
            for (Hiukkanen& h : k.hiukkaset) {
                Vec3 d = h.sijainti - pallon_keskus;
                double p = pituus(d);
                if (p >= pallon_sade || h.kaanteismassa == 0) continue;
                Vec3 n = (1 / p) * d;
                h.sijainti = pallon_keskus + pallon_sade * n;
                Vec3 liike = h.sijainti - h.edellinen;
                Vec3 pintaa_pitkin = liike - piste(liike, n) * n;
                h.sijainti = h.sijainti - 0.3 * pintaa_pitkin;
            }
    }
    for (Hiukkanen& h : k.hiukkaset)
        h.nopeus = (1 / dt) * (h.sijainti - h.edellinen);
}
// @loppu pbd

// @alku energia
inline double energia(const Kangas& k, Vec3 painovoima) {
    double e = 0;
    for (const Hiukkanen& h : k.hiukkaset)
        if (h.kaanteismassa > 0)
            e += (0.5 * piste(h.nopeus, h.nopeus) -
                  piste(painovoima, h.sijainti)) / h.kaanteismassa;
    return e;
}
// @loppu energia
