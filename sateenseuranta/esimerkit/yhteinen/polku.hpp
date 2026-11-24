// Polunseuranta: renderöintiyhtälön Monte Carlo -ratkaisu.
#pragma once
#include <algorithm>
#include <cstdint>

#include "kamera.hpp"
#include "kohtaus.hpp"

// @alku asetukset
struct Asetukset {
    int pomput = 8;        // pomppujen enimmäismäärä
    bool suora = true;     // suora valaistus valon näytteellä (NEE)
    bool ruletti = true;   // venäläinen ruletti kolmannesta pompusta
    bool nayta_valot = true;  // valolähteet näkyvät suoraan kamerasta
};
struct Laskuri {
    long sateet = 0, polut = 0;
};
// @loppu asetukset

// @alku suora
// Suora valaistus: piste valolta pinta-alan mukaan, varjosäde ja
// pinta-alamitan muunnos avaruuskulmaksi (cos_valo / r^2).
inline Vari suora_valo(const Kohtaus& K, const Materiaali& m, Vec3 p,
                       const Kanta& kanta, Vec3 v, Pcg32& g,
                       Laskuri& laskuri) {
    if (K.valot.empty()) return {};
    double ala = K.valo_kertyma.back(), u = g.tasainen() * ala;
    auto it = std::upper_bound(K.valo_kertyma.begin(),
                               K.valo_kertyma.end(), u);
    auto i = std::min<std::size_t>(it - K.valo_kertyma.begin(),
                                   K.valot.size() - 1);
    const auto& valo = K.kolmiot[K.valot[i]];
    double s = std::sqrt(g.tasainen()), b = g.tasainen() * s;
    Vec3 q = (1 - s) * valo.muoto.a + (s - b) * valo.muoto.b +
             b * valo.muoto.c;                // tasainen piste kolmiolla
    Vec3 d = q - p;
    double r2 = piste(d, d);
    Vec3 l = (1 / std::sqrt(r2)) * d;
    double cos_valo = -piste(normaali(valo.muoto), l);
    double cos_pinta = piste(kanta.n, l);
    if (cos_valo <= 0 || cos_pinta <= 0) return {};
    ++laskuri.sateet;
    if (!nakyy(K, p, q)) return {};
    Vari f = brdf(m, kanta.paikalliseen(v), kanta.paikalliseen(l));
    double paino = cos_pinta * cos_valo * ala / r2;  // pdf = 1 / ala
    return paino * (f * K.materiaalit[valo.m].sateily);
}
// @loppu suora

// @alku polku
inline Vari radianssi(const Kohtaus& K, Sade s, Pcg32& g,
                      const Asetukset& a, Laskuri& laskuri) {
    Vari L{}, kerroin{1, 1, 1};
    bool sateily_mukaan = true;  // ei laskettu jo suorana valona
    ++laskuri.polut;
    for (int pomppu = 0;; ++pomppu) {
        ++laskuri.sateet;
        Osuma o = leikkaa(K, s);
        if (!o.osui()) {
            L = L + kerroin * K.tausta;
            break;
        }
        const Materiaali& m = K.materiaalit[o.m];
        bool etupuoli = piste(o.n, s.d) < 0;
        Vec3 n = etupuoli ? o.n : -o.n;      // tulopuolen normaali
        if (sateily_mukaan && etupuoli && (pomppu > 0 || a.nayta_valot))
            L = L + kerroin * m.sateily;
        if (pomppu >= a.pomput) break;
        Vec3 v = -s.d;
        if (m.laji == Materiaali::peili) {
            kerroin = kerroin * m.vari;
            s = {o.p + SIIRTO * n, heijasta(s.d, n)};
            sateily_mukaan = true;
            continue;
        }
        if (m.laji == Materiaali::lasi) {
            double eta = etupuoli ? 1 / m.taitekerroin : m.taitekerroin;
            double F = fresnel(piste(v, n), eta);
            auto t = taita(s.d, n, eta);
            if (t && g.tasainen() >= F)
                s = {o.p - SIIRTO * n, normalisoi(*t)};
            else
                s = {o.p + SIIRTO * n, heijasta(s.d, n)};
            kerroin = kerroin * m.vari;
            sateily_mukaan = true;
            continue;
        }
        Kanta akselit = kanta(n);
        Vec3 p = o.p + SIIRTO * n;
        if (a.suora) {
            L = L + kerroin * suora_valo(K, m, p, akselit, v, g, laskuri);
            sateily_mukaan = false;
        }
        Vec3 l;
        Vari w = poimi(m, akselit.paikalliseen(v), g, l);
        if (suurin(w) <= 0) break;
        kerroin = kerroin * w;
        if (a.ruletti && pomppu >= 2) {
            double jatko = std::min(0.95, suurin(kerroin));
            if (g.tasainen() >= jatko) break;
            kerroin = (1 / jatko) * kerroin;
        }
        s = {p, akselit.maailmaan(l)};
    }
    return L;
}
// @loppu polku

// @alku renderoi
// Jokaisella pikselillä on oma satunnaislukuvirta, joten tulos ei
// riipu siitä, missä järjestyksessä pikselit lasketaan.
inline Kehys renderoi(const Kohtaus& K, const Kamera& k, int naytteet,
                      std::uint64_t siemen, const Asetukset& a,
                      Laskuri& laskuri) {
    Kehys kuva(k.leveys, k.korkeus);
    for (int y = 0; y < k.korkeus; ++y)
        for (int x = 0; x < k.leveys; ++x) {
            Pcg32 g(siemen, static_cast<std::uint64_t>(y) * k.leveys + x);
            Vari summa{};
            for (int i = 0; i < naytteet; ++i) {
                // Kaksi lausetta: argumenttien laskentajärjestystä ei
                // ole määrätty, ja GCC ja Clang laskevat ne eri
                // järjestyksessä.
                double dx = g.tasainen(), dy = g.tasainen();
                Sade s = k.sade(x + dx, y + dy);
                summa = summa + radianssi(K, s, g, a, laskuri);
            }
            kuva(x, y) = (1.0 / naytteet) * summa;
        }
    return kuva;
}
// @loppu renderoi
