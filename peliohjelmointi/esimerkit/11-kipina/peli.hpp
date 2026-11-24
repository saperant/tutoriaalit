// Kipinä: pelaaja kerää kiteitä ja väistää ajelehtivia miinoja.
// Pelilogiikka ei tiedä mitään ikkunoista, kellosta eikä grafiikasta.
#pragma once
#include "pcg.hpp"

#include <cstdint>
#include <vector>

// @alku tila
constexpr double LEVEYS = 160.0, KORKEUS = 120.0;  // maailma pikseleinä
constexpr double DT = 1.0 / 60.0;                   // kiinteä aika-askel

struct Syote {  // toiminnot, ei näppäimiä
    bool vasen = false, oikea = false, ylos = false, alas = false;
};

struct Kappale {
    double x = 0, y = 0, vx = 0, vy = 0, sade = 0;
};

enum class Tapahtuma { KideKeratty, Osuma, PeliPaattyi };

struct Peli {
    explicit Peli(std::uint64_t siemen);
    void paivita(const Syote& s);  // yksi kiinteä askel
    std::uint64_t tarkistussumma() const;

    Kappale pelaaja;
    std::vector<Kappale> kiteet, miinat;
    int pisteet = 0, elamat = 3, ruutu = 0;
    double suoja = 0.0;  // haavoittumattomuus osuman jälkeen, sekunteja
    bool ohi = false;
    std::vector<Tapahtuma> tapahtumat;  // tämän askeleen tapahtumat

private:
    Kappale uusi_kide();
    Kappale uusi_miina();
    Pcg32 satunnainen_;
};
// @loppu tila
