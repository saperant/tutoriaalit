// Törmäysvaste impulssilla: kaksi palloa (tai pallo ja liikkumaton
// seinä) erotetaan ja niiden nopeudet muutetaan niin, että liikemäärä
// säilyy. Kimmokerroin e päättää, kuinka paljon liike-energiasta jää.
#include <cmath>
#include <print>

struct V2 {
    double x, y;
    V2 operator+(V2 o) const { return {x + o.x, y + o.y}; }
    V2 operator-(V2 o) const { return {x - o.x, y - o.y}; }
    V2 operator*(double k) const { return {x * k, y * k}; }
};
double piste(V2 a, V2 b) { return a.x * b.x + a.y * b.y; }

// @alku kappale
struct Pallo {
    V2 paikka, nopeus;
    double sade;
    double kaanteismassa;  // 1/m; 0 = liikkumaton (seinä, maasto)
};
// @loppu kappale

// @alku vaste
// Palauttaa true, jos pallot koskettivat. Kaksi vaihetta:
// 1) erotus: kappaleet työnnetään irti käänteismassojen suhteessa
// 2) vaste: nopeutta muutetaan törmäysnormaalin suunnassa impulssilla j
bool ratkaise(Pallo& a, Pallo& b, double kimmokerroin) {
    const V2 d = b.paikka - a.paikka;
    const double etaisyys = std::hypot(d.x, d.y);
    const double limitys = a.sade + b.sade - etaisyys;
    const double massat = a.kaanteismassa + b.kaanteismassa;
    if (limitys <= 0.0 || etaisyys == 0.0 || massat == 0.0) {
        return false;
    }
    const V2 n = d * (1.0 / etaisyys);  // normaali a:sta b:hen

    a.paikka = a.paikka - n * (limitys * a.kaanteismassa / massat);
    b.paikka = b.paikka + n * (limitys * b.kaanteismassa / massat);

    const double lahestyminen = piste(b.nopeus - a.nopeus, n);
    if (lahestyminen >= 0.0) {
        return true;  // erkanevat jo: ei impulssia
    }
    const double j = -(1.0 + kimmokerroin) * lahestyminen / massat;
    a.nopeus = a.nopeus - n * (j * a.kaanteismassa);
    b.nopeus = b.nopeus + n * (j * b.kaanteismassa);
    return true;
}
// @loppu vaste

double liikemaara_x(const Pallo& p) {
    return p.kaanteismassa > 0.0 ? p.nopeus.x / p.kaanteismassa : 0.0;
}
double energia(const Pallo& p) {
    return p.kaanteismassa > 0.0
               ? 0.5 * piste(p.nopeus, p.nopeus) / p.kaanteismassa
               : 0.0;
}

int main() {
    std::println("kevyt pallo (1 kg, 4 m/s) osuu raskaaseen "
                 "(3 kg, levossa):");
    for (double e : {1.0, 0.5, 0.0}) {
        Pallo a{{0.0, 0.0}, {4.0, 0.0}, 0.5, 1.0};
        Pallo b{{0.9, 0.0}, {0.0, 0.0}, 0.5, 1.0 / 3.0};
        const double p0 = liikemaara_x(a) + liikemaara_x(b);
        const double e0 = energia(a) + energia(b);
        ratkaise(a, b, e);
        std::println("  e = {:.1f}: nopeudet {:5.2f} ja {:4.2f} m/s, "
                     "liikemäärä {:.1f} -> {:.1f}, energiaa {:3.0f} %",
                     e, a.nopeus.x, b.nopeus.x, p0,
                     liikemaara_x(a) + liikemaara_x(b),
                     100.0 * (energia(a) + energia(b)) / e0);
    }

    std::println("pallo osuu liikkumattomaan seinään vinosti (e = 0.8):");
    Pallo pallo{{0.0, 0.0}, {3.0, -2.0}, 0.5, 1.0};
    Pallo seina{{0.9, 0.0}, {0.0, 0.0}, 0.5, 0.0};
    ratkaise(pallo, seina, 0.8);
    std::println("  nopeus (3.00, -2.00) -> ({:.2f}, {:.2f}), "
                 "paikka x = {:.2f}, seinä x = {:.2f}",
                 pallo.nopeus.x, pallo.nopeus.y, pallo.paikka.x,
                 seina.paikka.x);
}
