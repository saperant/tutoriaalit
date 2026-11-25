// Aika ja tikit: asiakkaan ja palvelimen kellot eivät ole samassa
// ajassa, eikä viive ole vakio. Asiakas arvioi palvelimen ajan
// kiertoviiveestä ja säätää omaa tahtiaan niin, että syötteet ehtivät
// palvelimelle juuri ennen tikkiä, jota ne koskevat.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <print>

#include "yhteinen/verkko.hpp"

// @alku kello
// Asiakas lähettää oman kellonaikansa t0. Palvelin vastaa omalla
// ajallaan ts, ja vastaus saapuu asiakkaan kellon hetkellä t1.
struct Nayte {
    std::int64_t kiertoviive;  // t1 - t0
    std::int64_t siirtyma;     // arvio: palvelimen kello - asiakkaan kello
};

constexpr Nayte nayte(std::int64_t t0, std::int64_t ts, std::int64_t t1) {
    const std::int64_t rtt = t1 - t0;
    // Oletus: meno ja paluu kestivät yhtä kauan. Vastauksen saapuessa
    // palvelimen kello on silloin ts + rtt / 2.
    return {rtt, ts + rtt / 2 - t1};
}

// Oletus pätee parhaiten näytteessä, jonka kiertoviive on pienin:
// siinä kumpikaan suunta ei jonottanut.
std::int64_t paras(const std::deque<Nayte>& ikkuna) {
    return std::ranges::min_element(ikkuna, {}, &Nayte::kiertoviive)
        ->siirtyma;
}
// @loppu kello

struct Kysely {
    std::int64_t t0, ts;
};

void kellon_arvio() {
    constexpr std::int64_t ERO = -123'456;  // palvelin - asiakas, tuntematon
    const Linkki linkki{.viive_ms = 40, .varina_ms = 30,
                        .havio_promille = 20};
    Kanava<Kysely> ylos(linkki, 31), alas(linkki, 32);
    std::deque<Nayte> ikkuna;
    std::int64_t n = 0, pienin = 1'000, suurin = 0;
    std::int64_t virhe1 = 0, suurin1 = 0, virhe8 = 0, suurin8 = 0;
    for (std::int64_t t = 0; t < 60'000; ++t) {  // t on palvelimen aika
        const std::int64_t asiakkaan_kello = t - ERO;
        if (t % 250 == 0) {
            ylos.laheta(t, {asiakkaan_kello, 0});
        }
        for (Kysely k : ylos.vastaanota(t)) {
            k.ts = t;
            alas.laheta(t, k);
        }
        for (const Kysely& k : alas.vastaanota(t)) {
            const Nayte x = nayte(k.t0, k.ts, asiakkaan_kello);
            ikkuna.push_back(x);
            if (ikkuna.size() > 8) {
                ikkuna.pop_front();
            }
            const std::int64_t v1 = std::abs(x.siirtyma - ERO);
            const std::int64_t v8 = std::abs(paras(ikkuna) - ERO);
            loki("K {} {} {} {}", t, x.kiertoviive, x.siirtyma - ERO,
                 paras(ikkuna) - ERO);
            if (ikkuna.size() < 8) {
                continue;  // tilastoon vasta, kun ikkuna on täynnä
            }
            ++n;
            pienin = std::min(pienin, x.kiertoviive);
            suurin = std::max(suurin, x.kiertoviive);
            virhe1 += v1;
            suurin1 = std::max(suurin1, v1);
            virhe8 += v8;
            suurin8 = std::max(suurin8, v8);
        }
    }
    std::println("näytteitä {}, kiertoviive {}–{} ms", n, pienin, suurin);
    std::println("yksittäinen näyte:         virhe ka. {:2} ms, suurin "
                 "{:2} ms", virhe1 / n, suurin1);
    std::println("pienin kiertoviive 8:sta:  virhe ka. {:2} ms, suurin "
                 "{:2} ms", virhe8 / n, suurin8);
}

// @alku tahti
constexpr int TIKKI_MS = 20;
constexpr int TAVOITE = 2;  // syöte perille kaksi tikkiä etuajassa

// Palvelin kertoo jokaisesta syötteestä, montako tikkiä etuajassa se
// saapui (negatiivinen = myöhässä). Asiakas tasoittaa arvon ja
// nopeuttaa tai hidastaa omaa tikkiään viisi prosenttia, kunnes
// etumatka on tavoitteessa. Kello ei koskaan hyppää.
struct Tahdistin {
    int etumatka_x16 = 0;  // tasoitettu etumatka kuudestoistaosina

    int tikin_pituus(int mitattu) {
        etumatka_x16 += (mitattu * 16 - etumatka_x16) / 8;
        if (etumatka_x16 < TAVOITE * 16 - 12) {
            return TIKKI_MS - 1;  // nopeammin: etumatka kasvaa
        }
        if (etumatka_x16 > TAVOITE * 16 + 12) {
            return TIKKI_MS + 1;  // hitaammin: etumatka pienenee
        }
        return TIKKI_MS;
    }
};
// @loppu tahti

void tahdin_saato() {
    struct Syote {
        std::int64_t tikki;
    };
    struct Palaute {
        int etumatka;
    };
    Linkki linkki{.viive_ms = 40, .varina_ms = 10};
    Kanava<Syote> ylos(linkki, 41);
    Kanava<Palaute> alas(linkki, 42);
    Tahdistin tahdistin;
    std::int64_t asiakkaan_tikki = 0, seuraava = 0;
    int pituus = TIKKI_MS;
    int myohassa = 0, viimeisin = 0;
    std::println("{:>7} {:>9} {:>16} {:>13}", "sekunti", "myöhässä",
                 "etumatka lopussa", "tikin pituus");
    for (std::int64_t t = 0; t < 16'000; ++t) {
        if (t == 10'000) {
            // Reitti vaihtuu: yhden suunnan viive kasvaa 40 ms.
            ylos = Kanava<Syote>({.viive_ms = 80, .varina_ms = 10}, 43);
        }
        if (t >= seuraava) {  // asiakkaan tikki
            ylos.laheta(t, {asiakkaan_tikki++});
            seuraava += pituus;
        }
        for (const Syote& s : ylos.vastaanota(t)) {
            // Palvelin käsittelee syötteen s.tikki hetkellä
            // s.tikki * TIKKI_MS; sitä ennen saapunut on etuajassa.
            const std::int64_t vara_ms = s.tikki * TIKKI_MS - t;
            const auto etumatka = static_cast<int>(
                (vara_ms >= 0 ? vara_ms : vara_ms - TIKKI_MS + 1) /
                TIKKI_MS);  // pyöristys alaspäin myös negatiivisilla
            myohassa += vara_ms < 0;
            viimeisin = etumatka;
            alas.laheta(t, {etumatka});
        }
        for (const Palaute& p : alas.vastaanota(t)) {
            pituus = tahdistin.tikin_pituus(p.etumatka);
            loki("T {} {} {}", t, p.etumatka, pituus);
        }
        if (t % 1000 == 999) {
            const std::int64_t s = t / 1000 + 1;
            if (s <= 4 || (s >= 10 && s <= 14)) {
                std::println("{:>7} {:>9} {:>9} tikkiä {:>10} ms", s,
                             myohassa, viimeisin, pituus);
            }
            myohassa = 0;
        }
    }
}

int main(int argc, char**) {
    loki_paalla = argc > 1;
    kellon_arvio();
    tahdin_saato();
}
