// Asiakkaan ennustus ja palvelimen täsmäytys. Asiakas liikuttaa omaa
// hahmoaan heti ja lähettää syötteen numeroituna. Palvelimen vastaus
// kertoo virallisen sijainnin ja viimeisen käsitellyn syötteen; asiakas
// ottaa sen pohjaksi ja simuloi kuittaamattomat syötteet uudelleen.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <print>
#include <vector>

#include "yhteinen/verkko.hpp"

constexpr int TIKKI_MS = 20;
constexpr int NOPEUS = 5;  // senttimetriä tikissä

// @alku simulaatio
struct Syote {
    std::uint32_t numero;
    int suunta;  // -1, 0 tai 1
};
// Sama liikesääntö asiakkaalla ja palvelimella.
int liiku(int x, const Syote& s) { return x + s.suunta * NOPEUS; }
// @loppu simulaatio

struct SyotePaketti {
    std::vector<Syote> syotteet;  // uusin ja tarvittaessa aiemmat
};
struct TilaPaketti {
    int x;
    std::uint32_t kasitelty;  // viimeisin palvelimen käsittelemä syöte
};

struct Tulos {
    int korjauksia = 0, suurin_hyppy = 0;
    std::int64_t viive_summa = 0, viive_maara = 0;
};

Tulos aja(int havio, int toisto, bool tyonto) {
    const Linkki linkki{.viive_ms = 60, .varina_ms = 10,
                        .havio_promille = havio};
    Kanava<SyotePaketti> ylos(linkki, 3);
    Kanava<TilaPaketti> alas(linkki, 4);
    Pcg32 pelaaja(9);
    Tulos tulos;

    // Palvelin
    int palvelin_x = 0;
    std::uint32_t palvelin_kasitelty = 0;
    // Asiakas
    int ennuste = 0;
    std::deque<Syote> kesken;  // lähetetyt, kuittaamattomat
    std::vector<std::int64_t> lahetysaika;
    int suunta = 0;

    for (std::uint32_t tikki = 1; tikki <= 600; ++tikki) {
        const std::int64_t nyt = std::int64_t{tikki} * TIKKI_MS;
        if (pelaaja.valilta(30) == 0) {
            suunta = static_cast<int>(pelaaja.valilta(3)) - 1;
        }
        // @alku asiakas
        // Asiakas: syöte heti omaan hahmoon ja palvelimelle.
        const Syote s{tikki, suunta};
        ennuste = liiku(ennuste, s);
        kesken.push_back(s);
        lahetysaika.push_back(nyt);
        SyotePaketti paketti;
        const auto alku = kesken.size() > static_cast<std::size_t>(toisto)
                              ? kesken.end() - toisto
                              : kesken.begin();
        paketti.syotteet.assign(alku, kesken.end());
        ylos.laheta(nyt, paketti);
        // @loppu asiakas

        // @alku palvelin
        // Palvelin: käsittelee uudet syötteet järjestyksessä kerran.
        for (const SyotePaketti& p : ylos.vastaanota(nyt)) {
            for (const Syote& y : p.syotteet) {
                if (y.numero > palvelin_kasitelty) {
                    palvelin_x = liiku(palvelin_x, y);
                    palvelin_kasitelty = y.numero;
                }
            }
        }
        if (tyonto && tikki == 300) {
            palvelin_x += 200;  // räjähdys tönäisee: asiakas ei tiedä
        }
        alas.laheta(nyt, {palvelin_x, palvelin_kasitelty});
        // @loppu palvelin

        // @alku tasmaytys
        // Asiakas: virallinen tila pohjaksi, kuittaamattomat uudelleen.
        for (const TilaPaketti& t : alas.vastaanota(nyt)) {
            while (!kesken.empty() && kesken.front().numero <= t.kasitelty) {
                kesken.pop_front();
            }
            int x = t.x;
            for (const Syote& y : kesken) {
                x = liiku(x, y);
            }
            if (x != ennuste) {
                ++tulos.korjauksia;
                tulos.suurin_hyppy =
                    std::max(tulos.suurin_hyppy, std::abs(x - ennuste));
            }
            ennuste = x;
            if (t.kasitelty > 0) {
                tulos.viive_summa += nyt - lahetysaika[t.kasitelty - 1];
                ++tulos.viive_maara;
            }
        }
        // @loppu tasmaytys
    }
    return tulos;
}

int main() {
    struct Tapaus {
        const char* nimi;
        int havio, toisto;
        bool tyonto;
    };
    for (const Tapaus& t : {Tapaus{"hyvä yhteys", 0, 1, false},
                            Tapaus{"5 % hävikki", 50, 1, false},
                            Tapaus{"5 %, 3 syötettä", 50, 3, false},
                            Tapaus{"tönäisy", 0, 1, true}}) {
        const Tulos r = aja(t.havio, t.toisto, t.tyonto);
        std::println("{:<16} korjauksia {:>3}, suurin hyppy {:>3} cm, "
                     "kuittaus {} ms",
                     t.nimi, r.korjauksia, r.suurin_hyppy,
                     r.viive_summa / r.viive_maara);
    }
}
