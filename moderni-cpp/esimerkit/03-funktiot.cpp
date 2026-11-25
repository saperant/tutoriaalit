#include <print>
#include <string>

// @alku kuormitus
// Sama nimi, eri parametrit: kääntäjä valitsee argumentin tyypin mukaan.
std::string kuvaus(int x) { return "kokonaisluku " + std::to_string(x); }
std::string kuvaus(double x) { return "liukuluku " + std::to_string(x); }
std::string kuvaus(const std::string& s) { return "merkkijono " + s; }
// @loppu kuormitus

// @alku oletus
// Oletusargumentti: viimeiset parametrit voi jättää kutsusta pois.
std::string toista(const std::string& s, int kertaa = 2,
                   const std::string& erotin = " ")
{
    std::string tulos;
    for (int i = 0; i < kertaa; ++i) {
        if (i > 0) {
            tulos += erotin;
        }
        tulos += s;
    }
    return tulos;
}
// @loppu oletus

// @alku nimiavaruus
namespace geometria {

double ala(double leveys, double korkeus) { return leveys * korkeus; }

namespace yksikot {
constexpr double tuuma = 0.0254;   // metreinä
}

}   // namespace geometria
// @loppu nimiavaruus

int main()
{
    // @alku kutsut
    std::println("{}", kuvaus(42));
    std::println("{}", kuvaus(2.5));
    std::println("{}", kuvaus("hei"));

    std::println("{}", toista("hip"));
    std::println("{}", toista("hip", 3));
    std::println("{}", toista("hip", 3, "-"));
    // @loppu kutsut

    // @alku nimet
    std::println("{}", geometria::ala(2.0, 1.5));

    using geometria::yksikot::tuuma;   // tuo yhden nimen näkyviin
    std::println("{:.3f} m", 27 * tuuma);
    // @loppu nimet
}
