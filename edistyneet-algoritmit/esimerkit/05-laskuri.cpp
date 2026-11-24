// Binäärilaskurin tasoitettu hinta: bittien vaihtoja lasketaan, ja
// potentiaalina käytetään ykkösbittien määrää.
#include <bit>
#include <cstdint>
#include <print>

#include "testaus.hpp"

// @alku laskuri
// Kasvatus vaihtaa lopun ykköset nolliksi ja ensimmäisen nollan
// ykköseksi. Hinta on vaihdettujen bittien määrä.
struct Laskuri {
    std::uint32_t arvo = 0;

    int kasvata()
    {
        std::uint32_t uusi = arvo + 1;
        int hinta = std::popcount(arvo ^ uusi);
        arvo = uusi;
        return hinta;
    }

    int vahenna()
    {
        std::uint32_t uusi = arvo - 1;
        int hinta = std::popcount(arvo ^ uusi);
        arvo = uusi;
        return hinta;
    }
};
// @loppu laskuri

int main()
{
    // @alku tasoitettu
    // Phi = ykkösten määrä. Kasvatus, joka nollaa t ykköstä, maksaa t + 1
    // ja pienentää potentiaalia t - 1:llä: tasoitettu hinta on aina 2.
    constexpr long n = 1L << 20;
    Laskuri l;
    long yhteensa = 0;
    int suurin = 0;
    for (long i = 0; i < n; ++i) {
        int ennen = std::popcount(l.arvo);
        int hinta = l.kasvata();
        vaadi(hinta + std::popcount(l.arvo) - ennen == 2,
              "tasoitettu hinta ei ole 2");
        yhteensa += hinta;
        suurin = std::max(suurin, hinta);
    }
    std::println("{} kasvatusta: {} vaihtoa, {:.3f} vaihtoa/kasvatus, "
                 "suurin {}", n, yhteensa,
                 static_cast<double>(yhteensa) / n, suurin);
    // @loppu tasoitettu

    // @alku vuorottelu
    // Vähennys rikkoo analyysin: rajalla 2^20 - 1 <-> 2^20 jokainen
    // operaatio vaihtaa 21 bittiä.
    long vuorottelu = 0;
    for (int i = 0; i < 1000; ++i) {
        vuorottelu += l.vahenna();
        vuorottelu += l.kasvata();
    }
    std::println("1000 vähennystä ja kasvatusta vuorotellen: "
                 "{:.1f} vaihtoa/operaatio",
                 static_cast<double>(vuorottelu) / 2000);
    // @loppu vuorottelu
}
