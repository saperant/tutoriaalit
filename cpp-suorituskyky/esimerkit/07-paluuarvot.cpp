// Paluuarvot: pakollinen ja valinnainen kopion poisto sekä implisiittinen
// siirto.
#include <utility>

#include "seuranta.hpp"

// @alku prvalue
// Väliaikainen arvo palautetaan suoraan kutsujan muuttujaan (C++17:stä
// lähtien pakollista): ei kopiota eikä siirtoa.
Seurattava tee_prvalue()
{
    return Seurattava{"raportti"};
}
// @loppu prvalue

// @alku nrvo
// Nimetty paluuarvo (NRVO): kääntäjä saa rakentaa muuttujan suoraan
// kutsujan tilaan. GCC ja Clang tekevät sen, kun palautettava muuttuja
// on yksikäsitteinen.
Seurattava tee_nrvo()
{
    Seurattava s{"raportti"};
    s.arvo += " (luonnos)";
    return s;
}
// @loppu nrvo

// @alku kaksi
// Kaksi eri muuttujaa: kumpaa ei voi rakentaa valmiiksi kutsujan
// tilaan, joten paluu siirtää (implisiittinen siirto).
Seurattava tee_kahdesta(bool ehto)
{
    Seurattava a{"a"};
    Seurattava b{"b"};
    if (ehto) {
        return a;
    }
    return b;
}

// Parametri siirretään paluuarvoksi, ei kopioida.
Seurattava kulje(Seurattava s)
{
    return s;
}
// @loppu kaksi

// @alku jasen
// Paikallisen olion jäsen ei ole "paikallinen muuttuja": se kopioidaan.
Seurattava tee_jasenesta()
{
    std::pair<Seurattava, int> pari{Seurattava{"jasen"}, 1};
    return pari.first;
}
// @loppu jasen

int main()
{
    // @alku kaytto
    Seurattava::raportoi("(alku)");
    auto a = tee_prvalue();
    Seurattava::raportoi("prvalue");
    auto b = tee_nrvo();
    Seurattava::raportoi("NRVO");
    auto c = tee_kahdesta(true);
    Seurattava::raportoi("kaksi muuttujaa");
    auto d = kulje(Seurattava{"x"});
    Seurattava::raportoi("parametri");
    auto e = tee_jasenesta();
    Seurattava::raportoi("jasen");
    a = tee_prvalue();
    Seurattava::raportoi("sijoitus olemassa olevaan");
    // @loppu kaytto
    std::printf("arvot: %s, %s, %s, %s, %s\n", a.arvo.c_str(),
                b.arvo.c_str(), c.arvo.c_str(), d.arvo.c_str(),
                e.arvo.c_str());
}
