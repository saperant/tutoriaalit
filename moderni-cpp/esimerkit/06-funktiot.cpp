#include <print>
#include <string>
#include <vector>

// @alku tulos
struct Tilasto {
    double pienin;
    double suurin;
    double keskiarvo;
};

// Lukee vektoria vakioviittauksen kautta ja palauttaa tuloksen arvona.
Tilasto tilasto(const std::vector<double>& arvot)
{
    Tilasto t{arvot.front(), arvot.front(), 0.0};
    double summa = 0.0;
    for (double x : arvot) {
        t.pienin = x < t.pienin ? x : t.pienin;
        t.suurin = x > t.suurin ? x : t.suurin;
        summa += x;
    }
    t.keskiarvo = summa / static_cast<double>(arvot.size());
    return t;
}
// @loppu tulos

// @alku paluutyyppi
// Suurikin paluuarvo palautetaan arvona: kopiota ei synny.
std::vector<std::string> otsikot()
{
    std::vector<std::string> tulos{"pienin", "suurin", "keskiarvo"};
    return tulos;
}

// Paluutyypin voi jättää kääntäjän pääteltäväksi tai kirjoittaa
// nuolella parametrien jälkeen.
auto nelio(double x) { return x * x; }
auto puolikas(int x) -> double { return x / 2.0; }
// @loppu paluutyyppi

int main()
{
    // @alku kaytto
    std::vector<double> mittaukset{21.5, 19.0, 23.5, 20.0};
    auto [pienin, suurin, keskiarvo] = tilasto(mittaukset);

    auto nimet = otsikot();
    std::println("{}: {}", nimet[0], pienin);
    std::println("{}: {}", nimet[1], suurin);
    std::println("{}: {}", nimet[2], keskiarvo);
    std::println("{} {}", nelio(1.5), puolikas(5));
    // @loppu kaytto
}
