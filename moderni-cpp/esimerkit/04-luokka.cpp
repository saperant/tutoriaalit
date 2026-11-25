#include <numeric>
#include <print>
#include <stdexcept>

// @alku rakenne
struct Suorakulmio {
    double leveys = 0.0;
    double korkeus = 0.0;

    // Jäsenfunktio näkee olion jäsenet suoraan.
    double ala() const { return leveys * korkeus; }   // ei muuta oliota

    void skaalaa(double kerroin)                      // muuttaa oliota
    {
        leveys *= kerroin;
        korkeus *= kerroin;
    }
};
// @loppu rakenne

// @alku luokka
class Murtoluku {
public:
    Murtoluku(int osoittaja, int nimittaja)
        : osoittaja_{osoittaja}, nimittaja_{nimittaja}   // alustuslista
    {
        if (nimittaja_ == 0) {
            throw std::invalid_argument{"nimittäjä ei saa olla nolla"};
        }
        sievenna();
    }

    int osoittaja() const { return osoittaja_; }
    int nimittaja() const { return nimittaja_; }

    void kerro(int kerroin)
    {
        osoittaja_ *= kerroin;
        sievenna();
    }

private:
    void sievenna()
    {
        if (nimittaja_ < 0) {
            osoittaja_ = -osoittaja_;
            nimittaja_ = -nimittaja_;
        }
        int tekija = std::gcd(osoittaja_, nimittaja_);
        osoittaja_ /= tekija;
        nimittaja_ /= tekija;
    }

    int osoittaja_;
    int nimittaja_;
};
// @loppu luokka

// @alku operaattorit
Murtoluku operator+(const Murtoluku& a, const Murtoluku& b)
{
    return Murtoluku{a.osoittaja() * b.nimittaja()
                         + b.osoittaja() * a.nimittaja(),
                     a.nimittaja() * b.nimittaja()};
}

bool operator==(const Murtoluku& a, const Murtoluku& b)
{
    return a.osoittaja() == b.osoittaja()
           && a.nimittaja() == b.nimittaja();
}
// @loppu operaattorit

void tulosta(const Murtoluku& m)
{
    std::println("{}/{}", m.osoittaja(), m.nimittaja());
}

int main()
{
    // @alku rakenne-kaytto
    Suorakulmio s{2.0, 3.0};
    s.skaalaa(2.0);
    std::println("{} x {}, ala {}", s.leveys, s.korkeus, s.ala());

    const Suorakulmio vakio{1.0, 1.0};
    std::println("{}", vakio.ala());   // const-jäsenfunktio käy
    // vakio.skaalaa(2.0);             // ei käänny: olio on vakio
    // @loppu rakenne-kaytto

    // @alku luokka-kaytto
    Murtoluku puoli{2, 4};      // muodostin sieventää: 1/2
    tulosta(puoli);
    puoli.kerro(3);
    tulosta(puoli);

    try {
        Murtoluku virheellinen{1, 0};
        tulosta(virheellinen);
    } catch (const std::invalid_argument& virhe) {
        std::println("virhe: {}", virhe.what());
    }
    // @loppu luokka-kaytto

    // @alku operaattorit-kaytto
    Murtoluku summa = Murtoluku{1, 2} + Murtoluku{1, 3};
    tulosta(summa);
    std::println("{}", summa == Murtoluku{10, 12});
    // @loppu operaattorit-kaytto
}
