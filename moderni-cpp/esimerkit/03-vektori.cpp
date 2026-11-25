#include <algorithm>
#include <print>
#include <stdexcept>
#include <vector>

// @alku summa
double summa(const std::vector<double>& arvot)
{
    double tulos = 0.0;
    for (double x : arvot) {   // jokainen alkio vuorollaan
        tulos += x;
    }
    return tulos;
}
// @loppu summa

int main()
{
    // @alku perus
    std::vector<double> arvot{2.5, 4.0};
    arvot.push_back(1.5);   // kasvaa tarpeen mukaan
    arvot.push_back(8.0);
    std::println("{} alkiota, ensimmäinen {}, viimeinen {}",
                 arvot.size(), arvot.front(), arvot.back());
    arvot[1] = 3.0;         // indeksointi kuten taulukossa
    std::println("summa {}", summa(arvot));
    // @loppu perus

    // @alku kopio
    std::vector<double> kopio = arvot;   // kopioi kaikki alkiot
    kopio.pop_back();
    std::println("{} ja {} alkiota", arvot.size(), kopio.size());
    // @loppu kopio

    // @alku iteraattorit
    for (auto it = arvot.begin(); it != arvot.end(); ++it) {
        *it *= 2.0;   // iteraattori osoittaa alkioon kuten osoitin
    }

    std::sort(arvot.begin(), arvot.end());
    auto kohta = std::find(arvot.begin(), arvot.end(), 5.0);
    if (kohta != arvot.end()) {
        std::println("5.0 on indeksissä {}", kohta - arvot.begin());
    }

    for (double& x : arvot) {   // viittaus: alkiota voi muuttaa
        x += 1.0;
    }
    for (double x : arvot) {
        std::print("{} ", x);
    }
    std::println("");
    // @loppu iteraattorit

    // @alku poikkeus
    try {
        std::println("{}", arvot.at(10));   // at() tarkistaa indeksin
    } catch (const std::out_of_range&) {
        std::println("virhe: indeksi on alueen ulkopuolella");
    }
    // @loppu poikkeus
}
