// Pelisilmukan runko: syöte, päivitys ja piirto vuorotellen.
// Ruudut ajetaan ilman oikeaa kelloa, jotta tuloste on toistettava.
#include <print>

// @alku tila
struct Pallo {
    double x = 0.0;   // metreinä
    double vx = 3.0;  // metriä sekunnissa
};

struct Syote {
    bool kaanny = false;
};
// @loppu tila

// @alku silmukka
void kasittele_syote(Syote& s, int ruutu) {
    s.kaanny = (ruutu == 3);  // "pelaaja painaa nappia" ruudulla 3
}

void paivita(Pallo& p, const Syote& s, double dt) {
    if (s.kaanny) {
        p.vx = -p.vx;
    }
    p.x += p.vx * dt;
}

void piirra(const Pallo& p, int ruutu) {
    std::println("ruutu {}: x = {:5.2f} m", ruutu, p.x);
}

int main() {
    Pallo pallo;
    Syote syote;
    constexpr double dt = 1.0 / 4.0;  // neljä päivitystä sekunnissa
    for (int ruutu = 0; ruutu < 6; ++ruutu) {
        kasittele_syote(syote, ruutu);
        paivita(pallo, syote, dt);
        piirra(pallo, ruutu);
    }
}
// @loppu silmukka
