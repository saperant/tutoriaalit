// Kaatuminen ja palautuminen: mikä kuitattu tieto säilyy, kun palvelin
// kaatuu ja käynnistyy uudelleen? Neljä tapaa käsitellä pysyvää tilaa.
#include <cstdio>
#include <memory>
#include <vector>

#include "yhteinen/simulaattori.hpp"

struct Viesti {
    bool kuittaus;
    int nro;
};

// @alku levy
// Pysyvä tila säilyy kaatumisen yli; kirjoitus levylle maksaa
// (simuloitu fsync).
struct Levy {
    long laskuri = 0;
    long kirjoituksia = 0;
};
// @loppu levy

enum class Tapa { Haihtuva, Pysyva, Ryhma, RyhmaHeti };

// @alku palvelin
class Palvelin final : public Solmu<Viesti> {
public:
    static constexpr Aika VALI = 50;   // ryhmäkirjoituksen väli

    Palvelin(Tapa tapa, Levy& levy)
        : tapa_(tapa), levy_(levy), laskuri_(levy.laskuri) {}

    void kaynnisty(Yhteys<Viesti>& y) override {
        if (tapa_ == Tapa::Ryhma || tapa_ == Tapa::RyhmaHeti)
            y.ajasta(VALI, 0);
    }

    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        ++laskuri_;
        switch (tapa_) {
        case Tapa::Haihtuva:               // vain muistiin
            y.laheta(lahettaja, {true, v.nro});
            break;
        case Tapa::Pysyva:                 // levylle ennen kuittausta
            kirjoita();
            y.laheta(lahettaja, {true, v.nro});
            break;
        case Tapa::Ryhma:                  // kuittaus vasta kirjoituksen
            odottavat_.push_back({lahettaja, v.nro});   // jälkeen
            break;
        case Tapa::RyhmaHeti:              // virhe: kuittaus ennen
            y.laheta(lahettaja, {true, v.nro});         // kirjoitusta
            break;
        }
    }

    void ajastin(Yhteys<Viesti>& y, int) override {
        kirjoita();
        for (auto [kohde, nro] : odottavat_) y.laheta(kohde, {true, nro});
        odottavat_.clear();
        y.ajasta(VALI, 0);
    }

    long laskuri() const { return laskuri_; }

private:
    void kirjoita() {
        levy_.laskuri = laskuri_;
        ++levy_.kirjoituksia;
    }
    struct Odottava {
        int kohde, nro;
    };
    Tapa tapa_;
    Levy& levy_;
    long laskuri_;                     // haihtuva kopio
    std::vector<Odottava> odottavat_;  // haihtuva
};
// @loppu palvelin

class Asiakas final : public Solmu<Viesti> {
public:
    void kaynnisty(Yhteys<Viesti>& y) override { y.ajasta(10, 0); }
    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        ++kuitatut;
        viive_summa += y.kello() - lahetetty_[static_cast<size_t>(v.nro)];
    }
    void ajastin(Yhteys<Viesti>& y, int) override {
        if (y.kello() >= 2000) return;
        lahetetty_.push_back(y.kello());
        y.laheta(1, {false, static_cast<int>(lahetetty_.size()) - 1});
        y.ajasta(10, 0);
    }
    long kuitatut = 0;
    Aika viive_summa = 0;
private:
    std::vector<Aika> lahetetty_;
};

// @alku koe
void koe(const char* nimi, Tapa tapa) {
    Verkkoasetukset a{.viive_min = 1, .viive_max = 5};
    Simulaattori<Viesti, Levy> sim(2, 1, a,
        [tapa](int i, Levy& levy) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == 0) return std::make_unique<Asiakas>();
            return std::make_unique<Palvelin>(tapa, levy);
        });
    sim.kun(1234, [&] { sim.kaada(1); });
    sim.kun(1300, [&] { sim.kaynnista(1); });
    sim.aja(2500);
    auto* as = sim.solmu<Asiakas>(0);
    long arvo = sim.solmu<Palvelin>(1)->laskuri();
    std::printf("%-11s %8ld %6ld %9ld %10ld %9lld\n", nimi, as->kuitatut,
                arvo, as->kuitatut - arvo, sim.levy(1).kirjoituksia,
                static_cast<long long>(as->viive_summa / as->kuitatut));
}
// @loppu koe

int main() {
    std::printf("tapa        kuitattu  arvo  kadonnut  "
                "kirjoitus  viive ms\n");
    koe("haihtuva", Tapa::Haihtuva);
    koe("pysyva", Tapa::Pysyva);
    koe("ryhma", Tapa::Ryhma);
    koe("ryhma-heti", Tapa::RyhmaHeti);
}
