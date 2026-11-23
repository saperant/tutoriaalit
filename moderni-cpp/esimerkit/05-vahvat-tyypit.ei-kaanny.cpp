#include <compare>
#include <print>

// @alku tyypit
// Vahva tyyppi: kääre, joka antaa luvulle yksikön. Kääntäjä estää
// yksiköiden sekoittamisen, eikä kääre maksa ajoaikana mitään.
template <typename Yksikko>
class Maara {
public:
    constexpr explicit Maara(double arvo) : arvo_{arvo} {}
    constexpr double arvo() const { return arvo_; }

    constexpr Maara operator+(Maara toinen) const
    {
        return Maara{arvo_ + toinen.arvo_};
    }
    auto operator<=>(const Maara&) const = default;

private:
    double arvo_;
};

using Metrit = Maara<struct MetritTagi>;
using Sekunnit = Maara<struct SekunnitTagi>;

constexpr double nopeus(Metrit matka, Sekunnit aika)
{
    return matka.arvo() / aika.arvo();
}
// @loppu tyypit

int main()
{
    // @alku kaytto
    Metrit matka = Metrit{100.0} + Metrit{300.0};
    Sekunnit aika{50.0};
    std::println("{} m/s", nopeus(matka, aika));
#ifndef KORJATTU
    std::println("{}", nopeus(aika, matka));   // virhe: väärä järjestys
#endif
    // @loppu kaytto
}
