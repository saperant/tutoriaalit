// Yhteys UDP:n päällä: UDP:ssä ei ole yhteyksiä, joten peli rakentaa
// omansa. Palvelin varaa pelaajalle paikan vasta, kun asiakas on
// todistanut haasteella, että se todella vastaanottaa viestit
// ilmoittamassaan osoitteessa. Hiljainen yhteys puretaan
// aikakatkaisulla, ja elossaoloviestit pitävät sen auki.
#include <cstdint>
#include <map>
#include <optional>
#include <print>

#include "yhteinen/verkko.hpp"

// @alku viestit
enum class Tyyppi { Pyynto, Haaste, Vastaus, Hyvaksytty, Elossa };

struct Viesti {
    Tyyppi tyyppi;
    std::uint32_t osoite;  // lähettäjän (ilmoittama) osoite
    std::uint64_t luku;    // asiakkaan arpoma luku
    std::uint64_t haaste;  // palvelimen laskema tarkiste
};
// @loppu viestit

// @alku haaste
// Haaste lasketaan palvelimen salaisuudesta, osoitteesta ja asiakkaan
// luvusta. Palvelin ei tallenna sitä: vastauksen voi tarkistaa
// laskemalla saman uudelleen. Tämä sekoitusfunktio (SplitMix64) on
// vain esimerkki; oikea toteutus käyttää avaimellista tiivistettä
// (HMAC) ja lisää mukaan aikaleiman, jotta haaste vanhenee.
constexpr std::uint64_t sekoita(std::uint64_t x) {
    x += 0x9E3779B97F4A7C15ULL;
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL;
    x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL;
    return x ^ (x >> 31);
}

class Palvelin {
public:
    static constexpr std::int64_t AIKAKATKAISU_MS = 5000;

    // Palauttaa vastauksen, joka lähetetään viestin osoitteeseen.
    std::optional<Viesti> vastaanota(std::int64_t nyt, const Viesti& v) {
        switch (v.tyyppi) {
        case Tyyppi::Pyynto:
            // Ei tilaa eikä paikkaa: väärennetty osoite ei kuluta mitään.
            return Viesti{Tyyppi::Haaste, 0, v.luku, haaste(v)};
        case Tyyppi::Vastaus:
            if (v.haaste != haaste(v)) {
                ++hylatty;
                return std::nullopt;
            }
            yhteydet_[v.osoite] = nyt;  // paikka varataan vasta nyt
            return Viesti{Tyyppi::Hyvaksytty, 0, v.luku, 0};
        case Tyyppi::Elossa:
            if (const auto it = yhteydet_.find(v.osoite);
                it != yhteydet_.end()) {
                it->second = nyt;
            }
            return std::nullopt;
        default:
            return std::nullopt;
        }
    }
    // Yhteys, josta ei ole kuulunut mitään, puretaan.
    void tikki(std::int64_t nyt) {
        std::erase_if(yhteydet_, [nyt](const auto& y) {
            return nyt - y.second > AIKAKATKAISU_MS;
        });
    }
    bool yhdistetty(std::uint32_t osoite) const {
        return yhteydet_.contains(osoite);
    }
    std::size_t paikkoja() const { return yhteydet_.size(); }
    int hylatty = 0;

private:
    std::uint64_t haaste(const Viesti& v) const {
        return sekoita(salaisuus_ ^ sekoita(v.osoite) ^ v.luku);
    }
    std::uint64_t salaisuus_ = 0x5EEDC0FFEE123457ULL;
    std::map<std::uint32_t, std::int64_t> yhteydet_;  // viimeksi kuultu
};
// @loppu haaste

// @alku asiakas
// Asiakkaan tilakone. Jokainen vaihe lähetetään uudelleen, kunnes
// seuraava viesti saapuu: kättelyn viestitkin voivat kadota.
class Asiakas {
public:
    enum class Tila { Pyytaa, Vastaa, Yhdistetty };

    Asiakas(std::uint32_t osoite, std::uint64_t luku)
        : osoite_(osoite), luku_(luku) {}

    std::optional<Viesti> laheta(std::int64_t nyt) {
        const std::int64_t vali = tila == Tila::Yhdistetty ? 1000 : 200;
        if (nyt - viimeksi_ < vali) {
            return std::nullopt;
        }
        viimeksi_ = nyt;
        ++lahetyksia;
        switch (tila) {
        case Tila::Pyytaa:
            return Viesti{Tyyppi::Pyynto, osoite_, luku_, 0};
        case Tila::Vastaa:
            return Viesti{Tyyppi::Vastaus, osoite_, luku_, haaste_};
        default:
            return Viesti{Tyyppi::Elossa, osoite_, luku_, 0};
        }
    }
    void vastaanota(const Viesti& v) {
        if (v.luku != luku_) {
            return;  // ei vastaus tämän asiakkaan pyyntöön
        }
        if (v.tyyppi == Tyyppi::Haaste && tila == Tila::Pyytaa) {
            haaste_ = v.haaste;
            tila = Tila::Vastaa;
            viimeksi_ = -1000;  // vastaus lähtee heti
        } else if (v.tyyppi == Tyyppi::Hyvaksytty) {
            tila = Tila::Yhdistetty;
        }
    }
    Tila tila = Tila::Pyytaa;
    int lahetyksia = 0;

private:
    std::uint32_t osoite_;
    std::uint64_t luku_, haaste_ = 0;
    std::int64_t viimeksi_ = -1000;
};
// @loppu asiakas

int main(int argc, char**) {
    loki_paalla = argc > 1;
    // 1) Rehellinen asiakas huonolla yhteydellä: 20 % häviö.
    const Linkki huono{.viive_ms = 40, .varina_ms = 20,
                       .havio_promille = 200};
    Kanava<Viesti> ylos(huono, 5), alas(huono, 6);
    Palvelin palvelin;
    Asiakas asiakas(7, 0xABCDEF);
    std::int64_t yhdistyi = -1, katkesi = -1;
    for (std::int64_t nyt = 0; nyt < 20'000; ++nyt) {
        // Asiakas kaatuu hetkellä 8 s eikä lähetä enää mitään.
        if (nyt < 8000) {
            if (const auto v = asiakas.laheta(nyt)) {
                loki("L ylos {} {}", nyt, static_cast<int>(v->tyyppi));
                ylos.laheta(nyt, *v);
            }
        }
        for (const Viesti& v : ylos.vastaanota(nyt)) {
            loki("V ylos {} {}", nyt, static_cast<int>(v.tyyppi));
            if (const auto vastaus = palvelin.vastaanota(nyt, v)) {
                loki("L alas {} {}", nyt,
                     static_cast<int>(vastaus->tyyppi));
                alas.laheta(nyt, *vastaus);
            }
        }
        for (const Viesti& v : alas.vastaanota(nyt)) {
            loki("V alas {} {}", nyt, static_cast<int>(v.tyyppi));
            asiakas.vastaanota(v);
        }
        palvelin.tikki(nyt);
        if (yhdistyi < 0 && palvelin.yhdistetty(7)) {
            yhdistyi = nyt;
            std::println("{:5} ms: palvelin varasi paikan, asiakas oli "
                         "lähettänyt {} viestiä", nyt, asiakas.lahetyksia);
        }
        if (yhdistyi >= 0 && katkesi < 0 && !palvelin.yhdistetty(7)) {
            katkesi = nyt;
            std::println("{:5} ms: yhteys purettu, asiakas hiljeni "
                         "hetkellä 8000 ms", nyt);
        }
    }

    // 2) Väärennetyt lähdeosoitteet: vastaus menee osoitteeseen, jota
    // lähettäjä ei hallitse, joten haaste ei koskaan palaa.
    Palvelin uhri;
    int haasteita = 0;
    for (std::uint32_t i = 0; i < 1000; ++i) {
        const Viesti pyynto{Tyyppi::Pyynto, 1000 + i, i, 0};
        haasteita += uhri.vastaanota(0, pyynto).has_value();
        // Sokkona arvattu vastaus samasta väärennetystä osoitteesta.
        const Viesti arvaus{Tyyppi::Vastaus, 1000 + i, i, sekoita(i)};
        uhri.vastaanota(0, arvaus);
    }
    std::println("väärennetyt osoitteet: 1000 pyyntöä, haasteita {}, "
                 "arvauksia hylätty {}, paikkoja varattu {}", haasteita,
                 uhri.hylatty, uhri.paikkoja());
}
