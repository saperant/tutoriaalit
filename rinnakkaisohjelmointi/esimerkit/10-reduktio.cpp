// TSAN
// Rinnakkainen reduktio: osasummat säiekohtaisesti ja yhdistys lopuksi.
// Liukulukujen summa riippuu laskujärjestyksestä, joten tulos riippuu
// jaosta; kiinteä jako antaa silti saman tuloksen joka ajossa.
#include <cstddef>
#include <print>
#include <thread>
#include <vector>

// @alku reduktio
struct Kahan {             // kompensoitu summa: kerää pyöristysvirheen
    double summa = 0.0;
    double korjaus = 0.0;
    void lisaa(double x)
    {
        const double y = x - korjaus;
        const double t = summa + y;
        korjaus = (t - summa) - y;
        summa = t;
    }
};

template <class Summain>
double rinnakkainen_summa(const std::vector<double>& x, std::size_t osia)
{
    std::vector<Summain> osat(osia);
    {
        std::vector<std::jthread> saikeet;
        for (std::size_t s = 0; s < osia; ++s) {
            saikeet.emplace_back([&x, &osat, s, osia] {
                Summain oma;      // paikallinen, ei jaettu välimuistirivi
                for (std::size_t i = s * x.size() / osia;
                     i < (s + 1) * x.size() / osia; ++i) {
                    oma.lisaa(x[i]);
                }
                osat[s] = oma;    // yksi kirjoitus lopuksi
            });
        }
    }
    Summain yhteensa;
    for (const auto& o : osat) {
        yhteensa.lisaa(o.summa);
    }
    return yhteensa.summa;
}
// @loppu reduktio

struct Tavallinen {
    double summa = 0.0;
    void lisaa(double x) { summa += x; }
};

int main()
{
    // @alku kaytto
    std::vector<double> x(2'000'000);
    for (std::size_t i = 0; i < x.size(); ++i) {
        x[i] = 1.0 / static_cast<double>(i + 1);   // harmoninen sarja
    }
    for (std::size_t osia : {1u, 3u, 4u, 8u}) {
        std::println("{} osaa: tavallinen {:.17g}  Kahan {:.17g}", osia,
                     rinnakkainen_summa<Tavallinen>(x, osia),
                     rinnakkainen_summa<Kahan>(x, osia));
    }
    // @loppu kaytto
}
