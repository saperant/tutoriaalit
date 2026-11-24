// Viimeinen kirjoitus voittaa (LWW) fyysisillä kelloilla: kun kellot
// ovat eri ajassa, myöhempi kirjoitus voi hävitä, vaikka se olisi
// tehty edellisen kirjoituksen luvun jälkeen. Lamportin kello ja
// hybridikello säilyttävät syy-seuraussuhteen.
#include <cstdio>
#include <memory>

#include "yhteinen/kellot.hpp"
#include "yhteinen/simulaattori.hpp"

enum class Leima { Fyysinen, Lamport, Hybridi };

struct Viesti {
    enum class Laji { Luku, Arvo, Kirjoitus } laji;
    char arvo;
    Hlc leima;
};

// @alku varasto
// Rekisteri säilyttää arvon, jolla on suurin leima.
class Varasto final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        if (v.laji == Viesti::Laji::Luku) {
            y.laheta(lahettaja, {Viesti::Laji::Arvo, arvo, leima_});
        } else if (v.laji == Viesti::Laji::Kirjoitus && leima_ < v.leima) {
            arvo = v.arvo;
            leima_ = v.leima;
        }
    }
    char arvo = '-';
private:
    Hlc leima_{-1'000'000, 0};
};
// @loppu varasto

// @alku kirjoittaja
// A kirjoittaa hetkellä 100. B lukee hetkellä 130, näkee A:n arvon ja
// kirjoittaa sen jälkeen oman arvonsa: B:n kirjoitus on syy-seuraus-
// suhteessa A:n jälkeen, ja sen pitäisi voittaa.
class Kirjoittaja final : public Solmu<Viesti> {
public:
    Kirjoittaja(char arvo, Leima tapa) : arvo_(arvo), tapa_(tapa) {}

    void kaynnisty(Yhteys<Viesti>& y) override {
        y.ajasta(arvo_ == 'A' ? 100 : 130, 0);
    }
    void ajastin(Yhteys<Viesti>& y, int) override {
        if (arvo_ == 'A') kirjoita(y);
        else y.laheta(2, {Viesti::Laji::Luku, ' ', {}});
    }
    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        lamport_.vastaanotto(v.leima.l);              // nähty leima
        hybridi_.vastaanotto(y.kello(), v.leima);
        kirjoita(y);
    }
private:
    void kirjoita(Yhteys<Viesti>& y) {
        Hlc leima;
        switch (tapa_) {
        case Leima::Fyysinen: leima = {y.kello(), y.oma()}; break;
        case Leima::Lamport: leima = {lamport_.lahetys(), y.oma()}; break;
        case Leima::Hybridi: leima = hybridi_.tapahtuma(y.kello()); break;
        }
        y.laheta(2, {Viesti::Laji::Kirjoitus, arvo_, leima});
    }
    char arvo_;
    Leima tapa_;
    Lamport lamport_;
    Hybridikello hybridi_;
};
// @loppu kirjoittaja

int haviot(Leima tapa, Aika poikkeama) {
    int haviot = 0;
    for (std::uint64_t s = 1; s <= 200; ++s) {
        Verkkoasetukset a{.viive_min = 1, .viive_max = 10,
                          .poikkeama_max = poikkeama};
        Simulaattori<Viesti> sim(3, s, a,
            [tapa](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
                if (i == 2) return std::make_unique<Varasto>();
                return std::make_unique<Kirjoittaja>(i == 0 ? 'A' : 'B',
                                                     tapa);
            });
        sim.aja(1000);
        if (sim.solmu<Varasto>(2)->arvo != 'B') ++haviot;
    }
    return haviot;
}

int main() {
    std::printf("B:n kirjoitus hävisi (200 ajosta)\n");
    std::printf("poikkeama  fyysinen  lamport  hybridi\n");
    for (Aika p : {0, 10, 50, 200})
        std::printf("%6lld ms  %8d  %7d  %7d\n", static_cast<long long>(p),
                    haviot(Leima::Fyysinen, p), haviot(Leima::Lamport, p),
                    haviot(Leima::Hybridi, p));
}
