// Dynaamisen taulukon tasoitettu hinta: kasvatusstrategiat ja
// potentiaalifunktion tarkistus jokaisen lisäyksen jälkeen.
#include <cstdint>
#include <print>

#include "testaus.hpp"

// @alku malli
// Taulukon kustannusmalli: lisäys maksaa 1, ja kasvatus kopioi kaikki
// alkiot uuteen tilaan (hinta = koko). Kopioita lasketaan, alkioita ei
// tarvitse oikeasti tallentaa.
struct Taulukko {
    long koko = 0, kapasiteetti = 1, kopioita = 0;

    // Palauttaa lisäyksen todellisen hinnan.
    template <class Kasvatus>
    long lisaa(Kasvatus uusi_kapasiteetti)
    {
        long hinta = 1;
        if (koko == kapasiteetti) {
            kopioita += koko;
            hinta += koko;
            kapasiteetti = uusi_kapasiteetti(kapasiteetti);
        }
        ++koko;
        return hinta;
    }

    long poista(long kutistusraja)
    {
        long hinta = 1;
        --koko;
        if (koko > 0 && koko * kutistusraja <= kapasiteetti) {
            kopioita += koko;
            hinta += koko;
            kapasiteetti /= 2;
        }
        return hinta;
    }
};
// @loppu malli

int main()
{
    constexpr long n = 1'000'000;
    // @alku kasvatus
    auto kertoja2 = [](long c) { return 2 * c; };
    auto kertoja15 = [](long c) { return c + (c + 1) / 2; };
    auto lisays1000 = [](long c) { return c + 1000; };
    Taulukko a, b, c;
    for (long i = 0; i < n; ++i) {
        a.lisaa(kertoja2);
        b.lisaa(kertoja15);
    }
    for (long i = 0; i < n / 10; ++i) {   // vakiolisäys on liian hidas
        c.lisaa(lisays1000);
    }
    std::println("kasvatus x2:     {:.2f} kopiota/lisäys",
                 static_cast<double>(a.kopioita) / n);
    std::println("kasvatus x1.5:   {:.2f} kopiota/lisäys",
                 static_cast<double>(b.kopioita) / n);
    std::println("kasvatus +1000:  {:.2f} kopiota/lisäys (n/10 lisäystä)",
                 static_cast<double>(c.kopioita) / (n / 10));
    // @loppu kasvatus

    // @alku potentiaali
    // Potentiaali Phi = 2 koko - kapasiteetti (>= 0, kun taulukko on
    // vähintään puoliksi täynnä). Tasoitettu hinta on todellinen hinta
    // plus potentiaalin muutos, ja sen on oltava joka lisäyksellä <= 3.
    Taulukko t;
    long suurin_todellinen = 0, suurin_tasoitettu = 0;
    auto phi = [&] { return 2 * t.koko - t.kapasiteetti; };
    for (long i = 0; i < n; ++i) {
        long ennen = phi();
        long todellinen = t.lisaa(kertoja2);
        long tasoitettu = todellinen + phi() - ennen;
        vaadi(tasoitettu <= 3, "tasoitettu hinta ylittää 3");
        suurin_todellinen = std::max(suurin_todellinen, todellinen);
        suurin_tasoitettu = std::max(suurin_tasoitettu, tasoitettu);
    }
    std::println("suurin todellinen hinta {}, suurin tasoitettu {}",
                 suurin_todellinen, suurin_tasoitettu);
    // @loppu potentiaali

    // @alku kutistus
    // Vuorottelu rajalla: täytetään 2^k alkioon ja lisätään ja poistetaan
    // sitten vuorotellen. Kutistus puolillaan kopioi joka kerta.
    for (long raja : {2L, 4L}) {
        Taulukko k;
        for (long i = 0; i < 1024; ++i) {
            k.lisaa(kertoja2);
        }
        long ennen = k.kopioita;
        for (long i = 0; i < 1000; ++i) {
            k.lisaa(kertoja2);
            k.poista(raja);
        }
        std::println("kutistus kun koko <= kapasiteetti/{}: {:6} kopiota "
                     "1000 vuorottelussa", raja, k.kopioita - ennen);
    }
    // @loppu kutistus
}
