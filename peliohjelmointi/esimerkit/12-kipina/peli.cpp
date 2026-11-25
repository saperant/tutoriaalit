#include "peli.hpp"

#include <algorithm>
#include <bit>
#include <cmath>

namespace {

bool osuu(const Kappale& a, const Kappale& b) {
    const double dx = a.x - b.x, dy = a.y - b.y, r = a.sade + b.sade;
    return dx * dx + dy * dy < r * r;
}

// Kimpoaa seinistä: nopeus käännetään ja kappale palautetaan alueelle.
void kimpoa(Kappale& k) {
    if (k.x < k.sade || k.x > LEVEYS - k.sade) {
        k.vx = -k.vx;
        k.x = std::clamp(k.x, k.sade, LEVEYS - k.sade);
    }
    if (k.y < k.sade || k.y > KORKEUS - k.sade) {
        k.vy = -k.vy;
        k.y = std::clamp(k.y, k.sade, KORKEUS - k.sade);
    }
}

}  // namespace

Peli::Peli(std::uint64_t siemen) : satunnainen_(siemen) {
    pelaaja = {LEVEYS / 2, KORKEUS / 2, 0, 0, 4};
    for (int i = 0; i < 3; ++i) {
        kiteet.push_back(uusi_kide());
    }
    for (int i = 0; i < 2; ++i) {
        miinat.push_back(uusi_miina());
    }
}

Kappale Peli::uusi_kide() {
    return {satunnainen_.valilta(10, LEVEYS - 10),
            satunnainen_.valilta(10, KORKEUS - 10), 0, 0, 3};
}

Kappale Peli::uusi_miina() {
    // Miina syntyy reunalle, ei pelaajan päälle.
    const double kulma = satunnainen_.valilta(0.0, 6.2831853);
    return {satunnainen_.valilta(0, 1) < 0.5 ? 8.0 : LEVEYS - 8.0,
            satunnainen_.valilta(8, KORKEUS - 8), 25.0 * std::cos(kulma),
            25.0 * std::sin(kulma), 5};
}

// @alku paivita
void Peli::paivita(const Syote& s) {
    tapahtumat.clear();
    if (ohi) {
        return;
    }
    ++ruutu;
    // Pelaaja: kiihtyvyys syötteestä ja kitka (semi-implisiittinen).
    const double ax = (s.oikea - s.vasen) * 400.0;
    const double ay = (s.alas - s.ylos) * 400.0;
    pelaaja.vx = (pelaaja.vx + ax * DT) * 0.92;
    pelaaja.vy = (pelaaja.vy + ay * DT) * 0.92;
    pelaaja.x += pelaaja.vx * DT;
    pelaaja.y += pelaaja.vy * DT;
    kimpoa(pelaaja);

    for (Kappale& m : miinat) {
        m.x += m.vx * DT;
        m.y += m.vy * DT;
        kimpoa(m);
    }
    for (Kappale& k : kiteet) {
        if (osuu(pelaaja, k)) {
            pisteet += 10;
            k = uusi_kide();  // sama paikka taulukossa, uusi kide
            tapahtumat.push_back(Tapahtuma::KideKeratty);
        }
    }
    suoja = std::max(0.0, suoja - DT);
    if (suoja == 0.0) {
        for (const Kappale& m : miinat) {
            if (osuu(pelaaja, m)) {
                --elamat;
                suoja = 2.0;
                tapahtumat.push_back(Tapahtuma::Osuma);
                break;
            }
        }
    }
    if (ruutu % 600 == 0) {  // kymmenen sekunnin välein uusi miina
        miinat.push_back(uusi_miina());
    }
    if (elamat == 0) {
        ohi = true;
        tapahtumat.push_back(Tapahtuma::PeliPaattyi);
    }
}
// @loppu paivita

std::uint64_t Peli::tarkistussumma() const {
    std::uint64_t h = 1469598103934665603ULL;
    auto lisaa = [&](std::uint64_t arvo) {
        for (int i = 0; i < 8; ++i) {
            h = (h ^ ((arvo >> (8 * i)) & 0xffu)) * 1099511628211ULL;
        }
    };
    auto kappale = [&](const Kappale& k) {
        for (double d : {k.x, k.y, k.vx, k.vy}) {
            lisaa(std::bit_cast<std::uint64_t>(d));
        }
    };
    kappale(pelaaja);
    for (const auto& k : kiteet) {
        kappale(k);
    }
    for (const auto& m : miinat) {
        kappale(m);
    }
    lisaa(static_cast<std::uint64_t>(pisteet));
    lisaa(static_cast<std::uint64_t>(elamat));
    return h;
}
