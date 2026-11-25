// Lukitusaskelpelin asiakas: lähettää omat syötteensä palvelimelle ja
// simuloi pelin itse palvelimen vahvistamilla syötteillä. Lopuksi oma
// tarkistussumma verrataan palvelimen summaan.
#include <cstdlib>
#include <print>
#include <string>

#include "protokolla.hpp"

int main(int argc, char** argv) {
    if (argc != 3) {
        std::println(stderr, "käyttö: asiakas PELAAJA PORTTI");
        return 2;
    }
    const auto pelaaja = static_cast<std::uint8_t>(std::stoi(argv[1]) - 1);
    const auto palvelin =
        paikallinen(static_cast<std::uint16_t>(std::stoi(argv[2])));
    const std::vector<Syote> omat = syotteet(pelaaja + 1u);

    Soketti soketti;
    soketti.sido(0);
    Tila tila;
    std::uint32_t lahetetty = 0;
    int hiljaista = 0;
    // @alku asiakas
    for (;;) {
        // Enintään IKKUNA ruutua vahvistetun edellä: palvelimen
        // viestissä on silloin aina kaikki puuttuvat syötteet.
        while (lahetetty < RUUTUJA && lahetetty < tila.ruutu + IKKUNA) {
            ++lahetetty;
        }
        SyoteViesti v{pelaaja, lahetetty, {}};
        for (std::uint32_t k = 0; k < IKKUNA; ++k) {
            if (lahetetty >= IKKUNA - k) {
                v.syote[k] = omat[lahetetty - IKKUNA + k];
            }
        }
        soketti.laheta(kirjoita(v), palvelin);

        sockaddr_in lahettaja{};
        auto p = soketti.vastaanota(5, &lahettaja);
        if (!p) {
            if (++hiljaista > 2000) {  // 10 s ilman vastausta
                std::println(stderr, "asiakas {}: palvelin ei vastaa",
                             pelaaja + 1);
                return 1;
            }
            continue;
        }
        hiljaista = 0;
        const std::uint8_t laji = p->lue_u8();
        const TilaViesti t = lue_tila(*p, laji);
        // Simuloidaan vahvistetut ruudut, joita ei vielä ole laskettu.
        for (std::uint32_t f = tila.ruutu; f < t.ruutuja; ++f) {
            if (f + IKKUNA < t.ruutuja) {
                break;  // aukko: odotetaan seuraavaa viestiä
            }
            askel(tila, t.syote[f + IKKUNA - t.ruutuja]);
        }
        if (laji == LOPPU && tila.ruutu == t.ruutuja) {
            std::println("asiakas {}: {} ruutua, summa {:08x}, "
                         "sama kuin palvelimella: {}",
                         pelaaja + 1, tila.ruutu, tarkistussumma(tila),
                         tarkistussumma(tila) == t.summa);
            return 0;
        }
    }
    // @loppu asiakas
}
