// Pyyntö ja vastaus häviävän verkon yli: uudelleenlähetys
// aikakatkaisulla ja saman siemenen toistettavuus.
#include <cstdio>
#include <memory>
#include <string>

#include "yhteinen/simulaattori.hpp"

// @alku viesti
struct Viesti {
    enum class Laji { Pyynto, Vastaus } laji;
    int nro;
};
// @loppu viesti

// @alku asiakas
// Lähettää pyynnöt 1..N yksi kerrallaan ja lähettää pyynnön uudelleen,
// jos vastausta ei kuulu 30 ms:ssa.
class Asiakas final : public Solmu<Viesti> {
public:
    static constexpr int N = 5;
    static constexpr Aika AIKAKATKAISU = 30;

    void kaynnisty(Yhteys<Viesti>& y) override { laheta(y); }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.laji != Viesti::Laji::Vastaus || v.nro != nykyinen_)
            return;                       // vanha tai monistunut vastaus
        y.kirjaa("vastaus " + std::to_string(v.nro));
        if (++nykyinen_ <= N) laheta(y);
    }

    void ajastin(Yhteys<Viesti>& y, int nro) override {
        if (nro != nykyinen_ || nykyinen_ > N) return;  // jo vastattu
        ++uusinnat;
        y.kirjaa("aikakatkaisu " + std::to_string(nro));
        laheta(y);
    }

    int uusinnat = 0;
    int valmis() const { return nykyinen_ > N; }

private:
    void laheta(Yhteys<Viesti>& y) {
        y.laheta(1, {Viesti::Laji::Pyynto, nykyinen_});
        y.ajasta(AIKAKATKAISU, nykyinen_);
    }
    int nykyinen_ = 1;
};
// @loppu asiakas

// @alku palvelin
class Palvelin final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        ++kasitelty;
        y.laheta(lahettaja, {Viesti::Laji::Vastaus, v.nro});
    }
    int kasitelty = 0;
};
// @loppu palvelin

// @alku aja
struct Tulos {
    Aika valmistui;
    int uusinnat, kasitelty;
    Tilasto tilasto;
};

Tulos aja(std::uint64_t siemen, bool loki) {
    Verkkoasetukset a{.viive_min = 2, .viive_max = 20, .katoaa = 300,
                      .monistuu = 100};
    Simulaattori<Viesti> sim(2, siemen, a,
        [](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == 0) return std::make_unique<Asiakas>();
            return std::make_unique<Palvelin>();
        });
    sim.tulosta_loki(loki);
    Aika valmistui = -1;
    for (Aika t = 10; t <= 2000 && valmistui < 0; t += 10) {
        sim.aja(t);
        if (sim.solmu<Asiakas>(0)->valmis()) valmistui = t;
    }
    return {valmistui, sim.solmu<Asiakas>(0)->uusinnat,
            sim.solmu<Palvelin>(1)->kasitelty, sim.tilasto()};
}
// @loppu aja

int main() {
    // @alku main
    std::printf("Suoritus siemenellä 7:\n");
    aja(7, true);

    std::printf("\nsiemen  valmis  uusinnat  kasitelty  "
                "kadonnut  monistettu\n");
    for (std::uint64_t s : {7, 7, 8, 9, 10}) {
        Tulos r = aja(s, false);
        std::printf("%6llu  %6lld  %8d  %9d  %8ld  %10ld\n",
                    static_cast<unsigned long long>(s),
                    static_cast<long long>(r.valmistui), r.uusinnat,
                    r.kasitelty, r.tilasto.kadonnut,
                    r.tilasto.monistettu);
    }
    // @loppu main
}
