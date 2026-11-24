// Siirto, noexcept ja purkaja: kopioituvatko alkiot vektorin kasvaessa?
#include <cstdio>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#include "laskuri.hpp"

// @alku tyypit
// Nollan sääntö: kääntäjä tuottaa noexcept-siirron itse.
struct Tilaus {
    std::string asiakas;
    std::string tuote;
};

// Itse kirjoitettu siirto ilman noexcept-merkintää.
struct TilausEiNoexcept {
    std::string asiakas;
    std::string tuote;
    TilausEiNoexcept(std::string a, std::string t)
        : asiakas{std::move(a)}, tuote{std::move(t)} {}
    TilausEiNoexcept(const TilausEiNoexcept&) = default;
    TilausEiNoexcept(TilausEiNoexcept&& m)
        : asiakas{std::move(m.asiakas)}, tuote{std::move(m.tuote)} {}
};

// Pelkkä purkaja estää kääntäjää tuottamasta siirtoa lainkaan:
// "siirto" on silloin kopio.
struct TilausPurkaja {
    std::string asiakas;
    std::string tuote;
    ~TilausPurkaja() {}
};
// @loppu tyypit

// @alku tarkistus
static_assert(std::is_nothrow_move_constructible_v<Tilaus>);
static_assert(!std::is_nothrow_move_constructible_v<TilausEiNoexcept>);
static_assert(!std::is_nothrow_move_constructible_v<TilausPurkaja>);
// @loppu tarkistus

// @alku kasvatus
template <typename T>
void kasvata(const char* nimi)
{
    std::vector<T> v;
    laskuri::Jakso j;
    for (int i = 0; i < 1000; ++i) {
        v.push_back(T{std::string(20, 'a'), std::string(30, 'b')});
    }
    std::printf("  %-18s varauksia %5zu, tavuja %7zu\n", nimi, j.varaukset(),
                j.tavut());
}
// @loppu kasvatus

int main()
{
    std::printf("1000 tilausta vektoriin ilman reservea:\n");
    kasvata<Tilaus>("Tilaus");
    kasvata<TilausEiNoexcept>("TilausEiNoexcept");
    kasvata<TilausPurkaja>("TilausPurkaja");
}
