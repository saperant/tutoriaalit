// Kamera muuntaa maailman koordinaatit ruudun koordinaateiksi.
#pragma once
#include <algorithm>
#include <cmath>

// @alku kamera
struct Kamera {
    double x = 0.0, y = 0.0;  // näkymän vasen yläkulma maailmassa
    int leveys, korkeus;      // näkymän koko pikseleinä

    // Seuraa kohdetta, kun se poistuu näkymän keskeltä (kuollut alue),
    // mutta ei näytä maailman ulkopuolta.
    void seuraa(double kx, double maailman_leveys) {
        const double vasen = x + leveys * 0.35;
        const double oikea = x + leveys * 0.65;
        if (kx < vasen) {
            x -= vasen - kx;
        } else if (kx > oikea) {
            x += kx - oikea;
        }
        x = std::clamp(x, 0.0, maailman_leveys - leveys);
    }

    // Maailmasta ruudulle; pyöristys kokonaisiin pikseleihin tehdään
    // vasta tässä, jotta liike pysyy tasaisena.
    int ruudulle_x(double mx) const {
        return static_cast<int>(std::floor(mx - x));
    }
    int ruudulle_y(double my) const {
        return static_cast<int>(std::floor(my - y));
    }
};
// @loppu kamera
