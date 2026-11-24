// Viivat ja kolmiot pikseleiksi.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <utility>

#include "kuva.hpp"
#include "vektori.hpp"

// @alku bresenham
// Bresenhamin viiva kaikkiin suuntiin pelkillä kokonaisluvuilla.
// virhe = dx + dy pitää kirjaa siitä, kumpi askel vie lähemmäs
// ideaalista viivaa (dy on negatiivinen).
template <class F>
void viiva(int x0, int y0, int x1, int y1, F&& piirra) {
    int dx = std::abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
    int dy = -std::abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
    int virhe = dx + dy;
    while (true) {
        piirra(x0, y0);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * virhe;
        if (e2 >= dy) {  // askel x-suuntaan
            virhe += dy;
            x0 += sx;
        }
        if (e2 <= dx) {  // askel y-suuntaan
            virhe += dx;
            y0 += sy;
        }
    }
}
// @loppu bresenham

// @alku kiintopiste
// Kärkipisteet pyöristetään 1/256 pikselin ruudukkoon, kuten
// näytönohjaimissa. Sen jälkeen kaikki peittotestit ovat tarkkoja
// kokonaislukulaskuja.
constexpr long long ALI = 256;
struct Kiinto {
    long long x, y;
};
inline Kiinto kiintopisteeksi(Vec2 p) {
    return {std::llround(p.x * ALI), std::llround(p.y * ALI)};
}

// Reunafunktio: kolmion (a, b, p) kaksinkertainen ala. Ruudulla y
// kasvaa alaspäin, joten kaava on peilattu: arvo on positiivinen, kun
// p on näytöllä katsottuna reunan a -> b vasemmalla puolella, ja
// nolla, kun p on reunalla. Vastapäiväisen kolmion sisäpisteissä
// kaikki kolme reunafunktiota ovat positiivisia.
inline long long reuna(Kiinto a, Kiinto b, Kiinto p) {
    return (p.x - a.x) * (b.y - a.y) - (p.y - a.y) * (b.x - a.x);
}
// @loppu kiintopiste

// @alku vasen-yla
// Vastapäiväisessä kolmiossa yläreuna on vaakasuora ja kulkee
// vasemmalle; vasen reuna kulkee alaspäin (y kasvaa). Reunalle osuva
// pikseli kuuluu kolmioon vain, jos reuna on ylä- tai vasen reuna.
inline bool vasen_tai_yla(Kiinto a, Kiinto b) {
    long long dx = b.x - a.x, dy = b.y - a.y;
    return dy > 0 || (dy == 0 && dx < 0);
}
// @loppu vasen-yla

// @alku rasteroi
struct Bary {
    double l0, l1, l2;  // painot kärjille a, b ja c, summa 1
};

// Käy läpi kolmion rajaavan suorakulmion pikselit ja kutsuu
// fragmentti(x, y, painot) jokaiselle, jonka keskipiste on kolmiossa.
template <class F>
void rasteroi(Vec2 a, Vec2 b, Vec2 c, int leveys, int korkeus,
              F&& fragmentti, bool vasen_yla_saanto = true) {
    Kiinto p[3] = {kiintopisteeksi(a), kiintopisteeksi(b),
                   kiintopisteeksi(c)};
    long long ala = reuna(p[0], p[1], p[2]);
    if (ala == 0) return;  // surkastunut kolmio
    bool kaanna = ala < 0;  // kiertosuunta toisin päin: vaihda b ja c
    if (kaanna) {
        std::swap(p[1], p[2]);
        ala = -ala;
    }
    // Vinouma -1 tekee reunalla olevasta pikselistä ulkopuolisen.
    long long vino[3];
    for (int i = 0; i < 3; ++i) {
        Kiinto alku = p[(i + 1) % 3], loppu = p[(i + 2) % 3];
        vino[i] = !vasen_yla_saanto || vasen_tai_yla(alku, loppu) ? 0 : -1;
    }
    auto pienin = [](long long u, long long v, long long w) {
        return std::min({u, v, w});
    };
    auto suurin = [](long long u, long long v, long long w) {
        return std::max({u, v, w});
    };
    int x0 = static_cast<int>(std::max(
        0LL, pienin(p[0].x, p[1].x, p[2].x) / ALI - 1));
    int x1 = static_cast<int>(std::min<long long>(
        leveys - 1, suurin(p[0].x, p[1].x, p[2].x) / ALI + 1));
    int y0 = static_cast<int>(std::max(
        0LL, pienin(p[0].y, p[1].y, p[2].y) / ALI - 1));
    int y1 = static_cast<int>(std::min<long long>(
        korkeus - 1, suurin(p[0].y, p[1].y, p[2].y) / ALI + 1));
    for (int y = y0; y <= y1; ++y) {
        for (int x = x0; x <= x1; ++x) {
            Kiinto q = {(2 * x + 1) * ALI / 2, (2 * y + 1) * ALI / 2};
            long long w0 = reuna(p[1], p[2], q);
            long long w1 = reuna(p[2], p[0], q);
            long long w2 = reuna(p[0], p[1], q);
            if (w0 + vino[0] < 0 || w1 + vino[1] < 0 || w2 + vino[2] < 0)
                continue;
            double l0 = static_cast<double>(w0) / ala;
            double l1 = static_cast<double>(w1) / ala;
            double l2 = static_cast<double>(w2) / ala;
            if (kaanna) std::swap(l1, l2);
            fragmentti(x, y, Bary{l0, l1, l2});
        }
    }
}
// @loppu rasteroi

// @alku bary
// Samat painot liukuluvuin mielivaltaiselle pisteelle, esimerkiksi
// naapuripikselille derivaattoja varten.
inline Bary barysentriset(Vec2 a, Vec2 b, Vec2 c, Vec2 p) {
    auto e = [](Vec2 u, Vec2 v, Vec2 q) {
        return (q.x - u.x) * (v.y - u.y) - (q.y - u.y) * (v.x - u.x);
    };
    double ala = e(a, b, c);
    return {e(b, c, p) / ala, e(c, a, p) / ala, e(a, b, p) / ala};
}
// @loppu bary
