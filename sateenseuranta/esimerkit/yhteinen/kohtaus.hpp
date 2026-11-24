// Kohtaus: pallot, kolmiot, materiaalit ja valot.
#pragma once
#include <vector>

#include "materiaali.hpp"
#include "sade.hpp"

// @alku osuma
// Lähtöpisteen siirto pinnasta normaalin suuntaan (luku Leikkaukset).
constexpr double SIIRTO = 1e-7;

struct Osuma {
    double t = AARETON;
    Vec3 p, n;        // piste ja geometrinen normaali
    int m = -1;       // materiaalin indeksi
    bool osui() const { return t < AARETON; }
};
// @loppu osuma

// @alku kohtaus
struct Kohtaus {
    struct PalloEsine {
        Pallo muoto;
        int m;
    };
    struct KolmioEsine {
        Kolmio muoto;
        int m;
    };
    std::vector<Materiaali> materiaalit;
    std::vector<PalloEsine> pallot;
    std::vector<KolmioEsine> kolmiot;
    std::vector<int> valot;          // säteilevät kolmiot
    std::vector<double> valo_kertyma;  // pinta-alojen kertymä
    Vari tausta;                     // taivaan radianssi joka suuntaan

    int materiaali(Materiaali m) {
        materiaalit.push_back(m);
        return static_cast<int>(materiaalit.size()) - 1;
    }
    void lisaa(Pallo p, int m) { pallot.push_back({p, m}); }
    void lisaa(Kolmio k, int m) {
        kolmiot.push_back({k, m});
        if (luminanssi(materiaalit[m].sateily) > 0) {
            valot.push_back(static_cast<int>(kolmiot.size()) - 1);
            double ala = pituus(risti(k.b - k.a, k.c - k.a)) / 2;
            valo_kertyma.push_back(
                (valo_kertyma.empty() ? 0 : valo_kertyma.back()) + ala);
        }
    }
    // Suorakulmio a-b-c-d; etupuoli näkee kärjet vastapäivään.
    void suorakulmio(Vec3 a, Vec3 b, Vec3 c, Vec3 d, int m) {
        lisaa(Kolmio{a, b, c}, m);
        lisaa(Kolmio{a, c, d}, m);
    }
};
// @loppu kohtaus

// @alku leikkaa
// Lähin osuma raakahaulla: jokainen esine testataan. Pienissä
// kohtauksissa tämä riittää; suurissa käytetään BVH:ta.
inline Osuma leikkaa(const Kohtaus& K, const Sade& s,
                     double tmax = AARETON) {
    Osuma o;
    double lahin = tmax;
    for (const auto& e : K.pallot) {
        double t = leikkaa_pallo(e.muoto, s, 0, lahin);
        if (t < lahin) {
            lahin = t;
            o.t = t;
            o.p = kohta(s, t);
            o.n = (1 / e.muoto.r) * (o.p - e.muoto.keski);
            o.m = e.m;
        }
    }
    for (const auto& e : K.kolmiot) {
        KolmioOsuma k = leikkaa_kolmio(e.muoto, s, 0, lahin);
        if (k.t < lahin) {
            lahin = k.t;
            o.t = k.t;
            o.p = kohta(s, k.t);
            o.n = normaali(e.muoto);
            o.m = e.m;
        }
    }
    return o;
}
// Onko pisteiden p ja q välillä esteitä? Varjosäde.
inline bool nakyy(const Kohtaus& K, Vec3 p, Vec3 q) {
    Vec3 d = q - p;
    double etaisyys = pituus(d);
    Sade s{p, (1 / etaisyys) * d};
    return !leikkaa(K, s, etaisyys * (1 - 1e-6)).osui();
}
// @loppu leikkaa
