// Vesi korkeuskenttänä ja hiukkasallas roiskeille.
#pragma once
#include "vektori.hpp"

#include <cstdint>
#include <vector>

// @alku vesi
// Veden pinta ruudukkona: h on pinnan poikkeama lepotasosta ja v
// pinnan pystynopeus kussakin ruudussa.
struct Vesi {
    int n = 0;            // n x n ruutua
    double dx = 0.1;      // ruudun sivu (m)
    double aallonnopeus = 2.0;  // m/s
    double vaimennus = 0.3;     // 1/s
    std::vector<double> h, v;

    Vesi(int ruutuja, double ruudun_sivu)
        : n(ruutuja), dx(ruudun_sivu),
          h(static_cast<std::size_t>(ruutuja) * ruutuja),
          v(h.size()) {}
    std::size_t ruutu(int i, int j) const {  // reunan yli: reunaruutu
        i = i < 0 ? 0 : i >= n ? n - 1 : i;
        j = j < 0 ? 0 : j >= n ? n - 1 : j;
        return static_cast<std::size_t>(j) * n + i;
    }
    double& korkeus(int i, int j) { return h[ruutu(i, j)]; }
    double& nopeus(int i, int j) { return v[ruutu(i, j)]; }
    // Reunan yli katsottaessa palautetaan reunaruudun arvo: aalto
    // heijastuu seinästä, eikä vettä virtaa ulos.
    double lue(int i, int j) const { return h[ruutu(i, j)]; }
};
// @loppu vesi

// @alku vesiaskel
// Aaltoyhtälö: pinnan kiihtyvyys on verrannollinen siihen, kuinka
// paljon naapurit ovat ruutua korkeammalla. Puoli-implisiittinen
// Euler: ensin nopeus, sitten korkeus uudella nopeudella.
inline void askel(Vesi& w, double dt) {
    double k = w.aallonnopeus * w.aallonnopeus / (w.dx * w.dx);
    for (int j = 0; j < w.n; ++j)
        for (int i = 0; i < w.n; ++i) {
            double naapurit = w.lue(i - 1, j) + w.lue(i + 1, j) +
                              w.lue(i, j - 1) + w.lue(i, j + 1);
            std::size_t c = static_cast<std::size_t>(j) * w.n + i;
            w.v[c] += dt * k * (naapurit - 4 * w.h[c]);
        }
    double jaa = 1 - w.vaimennus * dt;
    for (std::size_t c = 0; c < w.h.size(); ++c) {
        w.v[c] *= jaa;
        w.h[c] += dt * w.v[c];
    }
}
inline double tilavuus(const Vesi& w) {
    double summa = 0;
    for (double h : w.h) summa += h;
    return summa * w.dx * w.dx;
}
// Pinnan korkeus maailman kohdassa (x, z); allas alkaa origosta.
inline double pinta(const Vesi& w, double x, double z) {
    return w.lue(static_cast<int>(x / w.dx), static_cast<int>(z / w.dx));
}
// @loppu vesiaskel

// @alku allas
// Hiukkasallas: kiinteä määrä paikkoja, ei muistinvarauksia pelin
// aikana. Kuollut hiukkanen korvataan viimeisellä elävällä.
struct Pisara {
    Vec3 sijainti, nopeus;
};
struct Pisarat {
    std::vector<Pisara> p;
    std::size_t elossa = 0;
    std::uint32_t siemen = 12345;

    explicit Pisarat(std::size_t paikkoja) : p(paikkoja) {}
    // Oma satunnaislukugeneraattori: sama siemen antaa saman roiskeen
    // jokaisella koneella (luku 13).
    double satunnainen() {
        siemen = siemen * 1664525u + 1013904223u;
        return (siemen >> 8) / 16777216.0;  // [0, 1)
    }
    void synnyta(Vec3 kohta, int maara, double vauhti) {
        for (int i = 0; i < maara && elossa < p.size(); ++i) {
            double kulma = 2 * PII * satunnainen();
            double sivulle = vauhti * 0.4 * satunnainen();
            p[elossa++] = {kohta,
                           {sivulle * std::cos(kulma),
                            vauhti * (0.5 + 0.5 * satunnainen()),
                            sivulle * std::sin(kulma)}};
        }
    }
};
// Pisarat lentävät heittoliikettä. Veteen osuva pisara kuolee ja
// tekee pintaan väreen: osumaruutu saa nopeuden alas ja sen neljä
// naapuria yhteensä saman verran ylös, joten tilavuus säilyy.
inline void askel(Pisarat& ps, Vesi& w, Vec3 painovoima, double dt) {
    for (std::size_t i = 0; i < ps.elossa;) {
        Pisara& a = ps.p[i];
        a.nopeus = a.nopeus + dt * painovoima;
        a.sijainti = a.sijainti + dt * a.nopeus;
        if (a.sijainti.y < pinta(w, a.sijainti.x, a.sijainti.z)) {
            int ci = static_cast<int>(a.sijainti.x / w.dx);
            int cj = static_cast<int>(a.sijainti.z / w.dx);
            w.nopeus(ci, cj) -= 0.2;
            w.nopeus(ci - 1, cj) += 0.05;
            w.nopeus(ci + 1, cj) += 0.05;
            w.nopeus(ci, cj - 1) += 0.05;
            w.nopeus(ci, cj + 1) += 0.05;
            a = ps.p[--ps.elossa];  // viimeinen elävä tilalle
        } else {
            ++i;
        }
    }
}
// @loppu allas
