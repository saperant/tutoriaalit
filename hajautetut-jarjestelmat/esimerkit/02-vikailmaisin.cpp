// Sykkeisiin perustuva vikailmaisin osittain synkronisessa verkossa:
// lyhyt aikaraja tunnistaa kaatumisen nopeasti mutta epäilee turhaan
// ruuhkan aikana, pitkä aikaraja ei epäile turhaan mutta on hidas.
#include <cstdio>
#include <memory>

#include "yhteinen/simulaattori.hpp"

struct Syke {
    int nro;
};

// @alku lahettaja
class Lahettaja final : public Solmu<Syke> {
public:
    static constexpr Aika VALI = 20;
    void kaynnisty(Yhteys<Syke>& y) override { y.ajasta(VALI, 0); }
    void vastaanota(Yhteys<Syke>&, int, const Syke&) override {}
    void ajastin(Yhteys<Syke>& y, int) override {
        y.laheta(1, {++nro_});
        y.ajasta(VALI, 0);
    }
private:
    int nro_ = 0;
};
// @loppu lahettaja

// @alku ilmaisin
// Epäilee lähettäjää, jos sykettä ei ole kuulunut aikarajan sisällä.
// Epäily perutaan, kun syke taas kuuluu.
class Ilmaisin final : public Solmu<Syke> {
public:
    explicit Ilmaisin(Aika aikaraja) : aikaraja_(aikaraja) {}

    void kaynnisty(Yhteys<Syke>& y) override { tarkista_myohemmin(y); }

    void vastaanota(Yhteys<Syke>& y, int, const Syke&) override {
        viimeisin_ = y.kello();
        if (epaily_) {
            epaily_ = false;
            ++perutut;
        }
    }

    void ajastin(Yhteys<Syke>& y, int) override {
        if (!epaily_ && y.kello() - viimeisin_ > aikaraja_) {
            epaily_ = true;
            ensimmainen_epaily = y.kello();
        }
        tarkista_myohemmin(y);
    }

    int perutut = 0;              // epäilyt, jotka osoittautuivat vääriksi
    Aika ensimmainen_epaily = -1;
    bool epailee() const { return epaily_; }

private:
    void tarkista_myohemmin(Yhteys<Syke>& y) { y.ajasta(5, 0); }
    Aika aikaraja_;
    Aika viimeisin_ = 0;
    bool epaily_ = false;
};
// @loppu ilmaisin

// @alku koe
// 0-1000 ms verkko on nopea, 1000-2000 ms ruuhkainen, sen jälkeen taas
// nopea. Lähettäjä kaatuu hetkellä 3000.
struct Tulos {
    int vaarat;
    Aika tunnistus;
};

Tulos koe(Aika aikaraja, std::uint64_t siemen) {
    Verkkoasetukset nopea{.viive_min = 1, .viive_max = 10};
    Verkkoasetukset ruuhka{.viive_min = 5, .viive_max = 120,
                           .katoaa = 50};
    Simulaattori<Syke> sim(2, siemen, nopea,
        [aikaraja](int i, Tyhja&) -> std::unique_ptr<Solmu<Syke>> {
            if (i == 0) return std::make_unique<Lahettaja>();
            return std::make_unique<Ilmaisin>(aikaraja);
        });
    sim.kun(1000, [&] { sim.verkko(ruuhka); });
    sim.kun(2000, [&] { sim.verkko(nopea); });
    sim.kun(3000, [&] { sim.kaada(0); });
    sim.aja(2999);
    auto* ilm = sim.solmu<Ilmaisin>(1);
    int vaarat = ilm->perutut + (ilm->epailee() ? 1 : 0);
    sim.aja(5000);
    Aika tunnistus = ilm->epailee() ? ilm->ensimmainen_epaily - 3000 : -1;
    return {vaarat, tunnistus};
}
// @loppu koe

int main() {
    std::printf("aikaraja  vaarat epailyt  tunnistusaika (ka. ms)\n");
    for (Aika raja : {30, 60, 120, 240}) {
        int vaarat = 0;
        Aika summa = 0;
        const int KOKEITA = 50;
        for (int s = 1; s <= KOKEITA; ++s) {
            Tulos t = koe(raja, static_cast<std::uint64_t>(s));
            vaarat += t.vaarat;
            summa += t.tunnistus;
        }
        std::printf("%5lld ms  %13.1f  %22lld\n",
                    static_cast<long long>(raja),
                    static_cast<double>(vaarat) / KOKEITA,
                    static_cast<long long>(summa / KOKEITA));
    }
}
