// Näppäimet kuvataan toiminnoiksi, ja toiminnoista tunnistetaan
// painallus, pito ja vapautus ruutujen välillä.
#include <array>
#include <bitset>
#include <print>
#include <string_view>
#include <utility>
#include <vector>

enum class Nappain { A, D, Vasen, Oikea, Valilyonti, Maara };
enum class Toiminto { Vasemmalle, Oikealle, Hyppy, Maara };

// @alku kartta
// Usea näppäin voi tuottaa saman toiminnon; kartan voi ladata
// asetuksista, jolloin pelaaja voi vaihtaa näppäimiä.
constexpr std::array<std::pair<Nappain, Toiminto>, 5> KARTTA{{
    {Nappain::A, Toiminto::Vasemmalle},
    {Nappain::Vasen, Toiminto::Vasemmalle},
    {Nappain::D, Toiminto::Oikealle},
    {Nappain::Oikea, Toiminto::Oikealle},
    {Nappain::Valilyonti, Toiminto::Hyppy},
}};

using Nappaimet = std::bitset<static_cast<int>(Nappain::Maara)>;
using Toiminnot = std::bitset<static_cast<int>(Toiminto::Maara)>;

Toiminnot toiminnoiksi(const Nappaimet& alhaalla) {
    Toiminnot t;
    for (auto [nappain, toiminto] : KARTTA) {
        if (alhaalla[static_cast<int>(nappain)]) {
            t.set(static_cast<int>(toiminto));
        }
    }
    return t;
}

struct Syotetila {
    Toiminnot nyt, edellinen;

    void paivita(const Nappaimet& alhaalla) {
        edellinen = nyt;
        nyt = toiminnoiksi(alhaalla);
    }
    bool painettu(Toiminto t) const {  // alas tällä ruudulla
        const int i = static_cast<int>(t);
        return nyt[i] && !edellinen[i];
    }
    bool pidetty(Toiminto t) const { return nyt[static_cast<int>(t)]; }
    bool vapautettu(Toiminto t) const {
        const int i = static_cast<int>(t);
        return !nyt[i] && edellinen[i];
    }
};
// @loppu kartta

Nappaimet nappaimet(std::initializer_list<Nappain> lista) {
    Nappaimet n;
    for (Nappain k : lista) {
        n.set(static_cast<int>(k));
    }
    return n;
}

int main() {
    using enum Nappain;
    const std::vector<Nappaimet> ruudut = {
        nappaimet({}), nappaimet({Valilyonti}), nappaimet({Valilyonti, D}),
        nappaimet({Oikea}), nappaimet({Oikea, D}), nappaimet({}),
    };
    Syotetila syote;
    for (std::size_t i = 0; i < ruudut.size(); ++i) {
        syote.paivita(ruudut[i]);
        std::println("ruutu {}: hyppy alas {:d} pito {:d} ylös {:d}, "
                     "oikealle {:d}",
                     i, syote.painettu(Toiminto::Hyppy),
                     syote.pidetty(Toiminto::Hyppy),
                     syote.vapautettu(Toiminto::Hyppy),
                     syote.pidetty(Toiminto::Oikealle));
    }
}
