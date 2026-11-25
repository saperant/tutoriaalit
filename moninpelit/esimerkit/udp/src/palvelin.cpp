// Lukitusaskelpelin palvelin: kerää molempien pelaajien syötteet UDP:llä,
// laskee ruudun vasta kun molemmat ovat perillä ja lähettää vahvistetut
// syötteet ja tilan tarkistussumman takaisin.
#include <chrono>
#include <cstdio>
#include <fstream>
#include <map>
#include <print>

#include "protokolla.hpp"

// Tilaviesti: vahvistettujen ruutujen määrä, summa ja viimeiset syötteet.
TilaViesti viesti(Laji laji, const std::vector<std::array<Syote, 2>>& v,
                  const Tila& tila) {
    TilaViesti t{laji, static_cast<std::uint32_t>(v.size()),
                 tarkistussumma(tila), {}};
    for (std::uint32_t k = 0; k < IKKUNA; ++k) {
        if (t.ruutuja >= IKKUNA - k) {
            t.syote[k] = v[t.ruutuja - IKKUNA + k];
        }
    }
    return t;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::println(stderr, "käyttö: palvelin PORTTITIEDOSTO");
        return 2;
    }
    Soketti soketti;
    soketti.sido(0);  // käyttöjärjestelmä valitsee vapaan portin
    {
        const std::string tilapainen = std::string(argv[1]) + ".tmp";
        std::ofstream(tilapainen) << soketti.portti() << '\n';
        std::rename(tilapainen.c_str(), argv[1]);  // valmis kerralla
    }

    // @alku silmukka
    std::array<std::vector<Syote>, 2> saadut;  // pelaajan syötteet
    std::array<std::optional<sockaddr_in>, 2> asiakkaat;
    std::vector<std::array<Syote, 2>> vahvistetut;
    Tila tila;
    auto viimeksi = std::chrono::steady_clock::now();
    while (vahvistetut.size() < RUUTUJA) {
        sockaddr_in lahettaja{};
        if (auto p = soketti.vastaanota(5, &lahettaja)) {
            if (p->lue_u8() != SYOTE) {
                continue;
            }
            const SyoteViesti v = lue_syote(*p);
            if (v.pelaaja > 1 || v.seuraava > RUUTUJA) {
                continue;  // virheellinen viesti hylätään
            }
            asiakkaat[v.pelaaja] = lahettaja;
            auto& omat = saadut[v.pelaaja];
            // Uudet syötteet ikkunasta; vanhat ovat jo tallessa.
            for (std::uint32_t k = 0; k < IKKUNA; ++k) {
                const auto ruutu = v.seuraava - IKKUNA + k;
                if (v.seuraava >= IKKUNA - k && ruutu == omat.size()) {
                    omat.push_back(v.syote[k]);
                }
            }
        }
        // Lasketaan kaikki ruudut, joihin molemmat syötteet ovat perillä.
        while (vahvistetut.size() < saadut[0].size() &&
               vahvistetut.size() < saadut[1].size()) {
            const auto f = vahvistetut.size();
            vahvistetut.push_back({saadut[0][f], saadut[1][f]});
            askel(tila, vahvistetut.back());
        }
        // @loppu silmukka
        // Tila lähtee 5 ms välein, vaikka mikään ei muuttuisi: kadonnut
        // tilaviesti korvautuu seuraavalla.
        const auto nyt = std::chrono::steady_clock::now();
        if (nyt - viimeksi >= std::chrono::milliseconds(5)) {
            viimeksi = nyt;
            const TilaViesti t = viesti(TILA, vahvistetut, tila);
            for (const auto& a : asiakkaat) {
                if (a) {
                    soketti.laheta(kirjoita(t), *a);
                }
            }
        }
    }
    // Lopetusviesti toistetaan, koska yksittäinen paketti voi kadota.
    const TilaViesti loppu = viesti(LOPPU, vahvistetut, tila);
    for (int i = 0; i < 20; ++i) {
        for (const auto& a : asiakkaat) {
            soketti.laheta(kirjoita(loppu), *a);
        }
        sockaddr_in ohita{};
        soketti.vastaanota(5, &ohita);
    }
    std::println("palvelin: {} ruutua, summa {:08x}", tila.ruutu,
                 tarkistussumma(tila));
}
