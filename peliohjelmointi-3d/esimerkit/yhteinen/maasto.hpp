// Esimerkkien maasto: korkeuskenttä, joka on muutaman kummun summa.
// Korkeus lasketaan vain peruslaskutoimituksilla, joten se on täsmälleen
// sama jokaisella koneella ja kääntäjällä.
#pragma once
#include "mallit.hpp"

// @alku korkeus
inline double maaston_korkeus(double x, double z) {
    struct Kumpu {
        double x, z, korkeus, leveys;
    };
    static constexpr Kumpu kummut[] = {
        {-6, -5, 3.0, 4.0}, {5, -8, 2.0, 3.0}, {8, 4, 1.5, 5.0},
        {-3, 7, 1.0, 3.0}};
    double h = 0;
    for (const Kumpu& k : kummut) {
        double d2 = ((x - k.x) * (x - k.x) + (z - k.z) * (z - k.z)) /
                    (k.leveys * k.leveys);
        h += k.korkeus / ((1 + d2) * (1 + d2));
    }
    return h;
}
// @loppu korkeus

// Neliön muotoinen maastoverkko origon ympärillä.
inline Verkko maastoverkko(int ruutuja, double sivu) {
    Verkko v;
    double askel = sivu / ruutuja;
    for (int j = 0; j <= ruutuja; ++j)
        for (int i = 0; i <= ruutuja; ++i) {
            double x = -sivu / 2 + i * askel, z = -sivu / 2 + j * askel;
            v.pisteet.push_back({x, maaston_korkeus(x, z), z});
        }
    for (int j = 0; j < ruutuja; ++j)
        for (int i = 0; i < ruutuja; ++i) {
            int a = j * (ruutuja + 1) + i, b = a + 1;
            int c = a + ruutuja + 1, d = c + 1;
            v.kolmiot.push_back({a, c, b});
            v.kolmiot.push_back({b, c, d});
        }
    return v;
}

// Maasto ruudutettuna: väri vaihtelee ruuduittain ja korkeuden mukaan.
inline void piirra_maasto(Piirtaja& p, const Verkko& v) {
    for (std::size_t i = 0; i < v.kolmiot.size(); ++i) {
        auto [a, b, c] = v.kolmiot[i];
        double h = v.pisteet[a].y;
        int n = static_cast<int>(
            std::lround(std::sqrt(v.kolmiot.size() / 2)));
        int ruutu = static_cast<int>(i / 2);
        bool tumma = ((ruutu / n) + (ruutu % n)) & 1;
        Vari vari = tumma ? Vari{112, 146, 100} : Vari{134, 166, 118};
        p.kolmio(v.pisteet[a], v.pisteet[b], v.pisteet[c],
                 himmenna(vari, 0.9 + 0.12 * h));
    }
}
