// CRDT:t juoruavassa verkossa: kolme replikaa päivittää laskuria ja
// joukkoa paikallisesti ja lähettää koko tilansa satunnaiselle
// naapurille. Verkko kadottaa, monistaa ja järjestää viestit
// uudelleen. Vertailukohtana laskuri, jonka arvo ratkaistaan
// "viimeinen kirjoitus voittaa" -säännöllä.
#include <cstdio>
#include <memory>
#include <string>

#include "yhteinen/crdt.hpp"
#include "yhteinen/simulaattori.hpp"

constexpr int N = 3;

// @alku tila
struct Lww {                     // arvo, (kello, replika)
    std::int64_t arvo = 0, kello = -1, replika = -1;
    void yhdista(const Lww& o) {
        if (o.kello > kello || (o.kello == kello && o.replika > replika))
            *this = o;
    }
};

struct Tila {
    PNLaskuri laskuri{N};
    ORJoukko joukko;
    Lww lww;
};
// @loppu tila

struct Yhteenveto {
    std::int64_t odotettu = 0;   // kaikkien muutosten summa
};

const char* TUOTTEET[] = {"kahvi", "leipa", "maito", "juusto"};

// @alku replika
class Replika final : public Solmu<Tila> {
public:
    explicit Replika(Yhteenveto& y) : yv_(y) {}
    void kaynnisty(Yhteys<Tila>& y) override {
        y.ajasta(10, 0);   // paikallinen muutos
        y.ajasta(20, 1);   // juoru
    }
    void vastaanota(Yhteys<Tila>&, int, const Tila& t) override {
        tila.laskuri.yhdista(t.laskuri);
        tila.joukko.yhdista(t.joukko);
        tila.lww.yhdista(t.lww);
    }
    void ajastin(Yhteys<Tila>& y, int laji) override {
        auto oma = static_cast<std::size_t>(y.oma());
        auto& sat = y.satunnainen();
        if (laji == 0 && y.kello() < 1000) {
            int op = static_cast<int>(sat.valilta(0, 3));
            if (op <= 1) {
                int d = op == 0 ? 1 : -1;
                if (d > 0) tila.laskuri.kasvata(oma);
                else tila.laskuri.vahenna(oma);
                yv_.odotettu += d;
                tila.lww = {tila.lww.arvo + d, y.kello(), y.oma()};
            } else {
                std::string t = TUOTTEET[sat.valilta(0, 3)];
                if (op == 2) tila.joukko.lisaa(oma, t);
                else tila.joukko.poista(t);
            }
            y.ajasta(10, 0);
        } else if (laji == 1) {
            int kohde = static_cast<int>(sat.valilta(0, N - 2));
            if (kohde >= y.oma()) ++kohde;             // joku muu
            y.laheta(kohde, tila);
            y.ajasta(20, 1);
        }
    }
    Tila tila;
private:
    Yhteenveto& yv_;
};
// @loppu replika

int main() {
    // @alku koe
    std::printf("                  PN-laskuri replikoissa\n");
    std::printf("siemen  odotettu    r0    r1    r2    LWW  "
                "joukot samat\n");
    for (std::uint64_t s = 1; s <= 5; ++s) {
        Yhteenveto yv;
        Verkkoasetukset a{.viive_min = 1, .viive_max = 40, .katoaa = 200,
                          .monistuu = 200, .poikkeama_max = 20};
        Simulaattori<Tila> sim(N, s, a,
            [&yv](int, Tyhja&) -> std::unique_ptr<Solmu<Tila>> {
                return std::make_unique<Replika>(yv);
            });
        sim.aja(2000);      // muutokset loppuvat 1000, juoru jatkuu
        auto& t0 = sim.solmu<Replika>(0)->tila;
        auto& t1 = sim.solmu<Replika>(1)->tila;
        auto& t2 = sim.solmu<Replika>(2)->tila;
        bool samat = t0.joukko == t1.joukko && t1.joukko == t2.joukko;
        std::printf("%6llu  %8lld  %4lld  %4lld  %4lld  %5lld  %s\n",
                    static_cast<unsigned long long>(s),
                    static_cast<long long>(yv.odotettu),
                    static_cast<long long>(t0.laskuri.arvo()),
                    static_cast<long long>(t1.laskuri.arvo()),
                    static_cast<long long>(t2.laskuri.arvo()),
                    static_cast<long long>(t0.lww.arvo),
                    samat ? "kylla" : "ei");
    }
    // @loppu koe

    // @alku lisays-voittaa
    std::printf("\nsamanaikainen lisays ja poisto:\n");
    ORJoukko a, b;
    a.lisaa(0, "maito");
    b.yhdista(a);              // b on nähnyt a:n lisäyksen
    b.poista("maito");         // b poistaa näkemänsä maidon
    a.lisaa(0, "maito");       // a lisää maidon uudelleen samaan aikaan
    a.yhdista(b);
    b.yhdista(a);
    std::printf("a: %s, b: %s\n", a.sisaltaa("maito") ? "maito" : "-",
                b.sisaltaa("maito") ? "maito" : "-");
    // @loppu lisays-voittaa
}
