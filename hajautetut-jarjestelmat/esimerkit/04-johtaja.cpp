// Johtaja–seuraaja-replikointi: asynkroninen, puolisynkroninen ja
// synkroninen kuittaus. Kun johtaja kaatuu ja seuraaja ylennetään,
// asynkronisesti kuitatut kirjoitukset voivat kadota. Kun seuraaja
// kaatuu, synkroninen replikointi pysäyttää kirjoitukset.
#include <cstdio>
#include <memory>
#include <set>
#include <vector>

#include "yhteinen/simulaattori.hpp"

enum class Tila { Asynkroninen, Puolisynkroninen, Synkroninen };

struct Viesti {
    enum class Laji { Kirjoitus, Replikoi, Kuittaus, Valmis } laji;
    int nro;
};

constexpr int JOHTAJA = 0, ASIAKAS = 3;

// @alku johtaja
// Asynkroninen johtaja kuittaa heti ja lähettää muutokset seuraajille
// eränä 50 ms välein. Muut lähettävät heti ja kuittaavat, kun riittävän
// moni seuraaja on vastannut.
class Johtaja final : public Solmu<Viesti> {
public:
    static constexpr Aika ERAVALI = 50;
    explicit Johtaja(Tila tila) : tila_(tila) {}

    void kaynnisty(Yhteys<Viesti>& y) override {
        if (tila_ == Tila::Asynkroninen) y.ajasta(ERAVALI, 0);
    }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Kirjoitus) {
            if (tila_ == Tila::Asynkroninen) {
                era_.push_back(v.nro);
                kuittaa(y, v.nro);
                return;
            }
            kuittauksia_.resize(static_cast<size_t>(v.nro) + 1, 0);
            replikoi(y, v.nro);
        } else if (tila_ != Tila::Asynkroninen) {   // seuraajan kuittaus
            int& k = kuittauksia_[static_cast<size_t>(v.nro)];
            ++k;
            int tarvitaan = tila_ == Tila::Synkroninen ? 2 : 1;
            if (k == tarvitaan) kuittaa(y, v.nro);
        }
    }

    void ajastin(Yhteys<Viesti>& y, int) override {
        for (int n : era_) replikoi(y, n);
        era_.clear();
        y.ajasta(ERAVALI, 0);
    }

private:
    void replikoi(Yhteys<Viesti>& y, int nro) {
        for (int s : {1, 2}) y.laheta(s, {Viesti::Laji::Replikoi, nro});
    }
    void kuittaa(Yhteys<Viesti>& y, int nro) {
        y.laheta(ASIAKAS, {Viesti::Laji::Valmis, nro});
    }
    Tila tila_;
    std::vector<int> kuittauksia_;
    std::vector<int> era_;          // haihtuva: katoaa kaatuessa
};
// @loppu johtaja

class Seuraaja final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        loki.insert(v.nro);
        y.laheta(lahettaja, {Viesti::Laji::Kuittaus, v.nro});
    }
    std::set<int> loki;
};

class Asiakas final : public Solmu<Viesti> {
public:
    void kaynnisty(Yhteys<Viesti>& y) override { y.ajasta(10, 0); }
    void ajastin(Yhteys<Viesti>& y, int) override {
        lahetetty_.push_back(y.kello());
        y.laheta(JOHTAJA, {Viesti::Laji::Kirjoitus,
                           static_cast<int>(lahetetty_.size()) - 1});
        if (y.kello() < 1500) y.ajasta(10, 0);
    }
    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        kuitatut.push_back(v.nro);
        viive += y.kello() - lahetetty_[static_cast<size_t>(v.nro)];
    }
    std::vector<int> kuitatut;
    Aika viive = 0;
private:
    std::vector<Aika> lahetetty_;
};

// @alku koe
struct Tulos {
    long kuitattu, menetetty;
    Aika viive;
};

// vika 0: johtaja kaatuu hetkellä 1000; vika 1: seuraaja 2 kaatuu
// hetkellä 500.
Tulos koe(Tila tila, int vika, std::uint64_t siemen) {
    Verkkoasetukset a{.viive_min = 1, .viive_max = 30};
    Simulaattori<Viesti> sim(4, siemen, a,
        [tila](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == JOHTAJA) return std::make_unique<Johtaja>(tila);
            if (i == ASIAKAS) return std::make_unique<Asiakas>();
            return std::make_unique<Seuraaja>();
        });
    if (vika == 0) sim.kun(1000, [&] { sim.kaada(JOHTAJA); });
    else sim.kun(500, [&] { sim.kaada(2); });
    sim.aja(2000);
    auto* as = sim.solmu<Asiakas>(ASIAKAS);
    long menetetty = 0;
    if (vika == 0) {   // ylennetään seuraaja, jolla on pisin loki
        auto* s1 = sim.solmu<Seuraaja>(1);
        auto* s2 = sim.solmu<Seuraaja>(2);
        auto* uusi = s1->loki.size() >= s2->loki.size() ? s1 : s2;
        for (int n : as->kuitatut)
            if (!uusi->loki.contains(n)) ++menetetty;
    }
    long k = static_cast<long>(as->kuitatut.size());
    return {k, menetetty, k ? as->viive / k : 0};
}
// @loppu koe

int main() {
    std::printf("keskiarvot 20 ajosta\n");
    std::printf("tila               johtaja kaatuu         "
                "seuraaja kaatuu\n");
    std::printf("                   kuitattu menetetty viive  kuitattu\n");
    const char* nimet[] = {"asynkroninen", "puolisynkroninen",
                           "synkroninen"};
    for (int t = 0; t < 3; ++t) {
        long kuitattu = 0, menetetty = 0, kuitattu2 = 0;
        Aika viive = 0;
        for (std::uint64_t s = 1; s <= 20; ++s) {
            Tulos a = koe(static_cast<Tila>(t), 0, s);
            Tulos b = koe(static_cast<Tila>(t), 1, s);
            kuitattu += a.kuitattu;
            menetetty += a.menetetty;
            viive += a.viive;
            kuitattu2 += b.kuitattu;
        }
        std::printf("%-18s %8ld %9.1f %5lld  %8ld\n", nimet[t],
                    kuitattu / 20, static_cast<double>(menetetty) / 20,
                    static_cast<long long>(
                    viive / 20), kuitattu2 / 20);
    }
}
