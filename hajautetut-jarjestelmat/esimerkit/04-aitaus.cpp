// Vuokra ja aitausmerkki: työntekijä, jonka vuokra on vanhentunut
// tauon aikana, kirjoittaa silti. Tallennus, joka tarkistaa
// aitausmerkin, hylkää vanhan haltijan kirjoituksen.
#include <algorithm>
#include <cstdio>
#include <memory>
#include <string>

#include "yhteinen/simulaattori.hpp"

struct Viesti {
    enum class Laji { Pyyda, Vuokra, Varattu, Kirjoita, Ok, Hylatty } laji;
    int merkki = 0;   // aitausmerkki
    int arvo = 0;     // kirjoitettava arvo
};

constexpr int LUKKO = 0, TALLENNUS = 1, TYO_A = 2;   // TYO_B = 3
constexpr Aika VUOKRA = 200;   // vuokran kesto ms

// @alku lukko
// Lukkopalvelu antaa vuokran yhdelle kerrallaan. Jokainen uusi vuokra
// saa edellistä suuremman aitausmerkin. Vuokra vanhenee itsestään:
// haltijan ei tarvitse (eikä se kaatuneena voi) palauttaa sitä.
class Lukkopalvelu final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti&) override {
        if (haltija_ != -1 && y.kello() < paattyy_) {
            y.laheta(lahettaja, {Viesti::Laji::Varattu});
            return;
        }
        haltija_ = lahettaja;
        paattyy_ = y.kello() + VUOKRA;
        ++merkki_;
        y.kirjaa("vuokra solmulle s" + std::to_string(lahettaja) +
                 ", merkki " + std::to_string(merkki_));
        y.laheta(lahettaja, {Viesti::Laji::Vuokra, merkki_});
    }

private:
    int haltija_ = -1;
    Aika paattyy_ = 0;
    int merkki_ = 0;
};
// @loppu lukko

// @alku tallennus
// Tallennus muistaa suurimman näkemänsä merkin. Aitaus päällä se
// hylkää kirjoituksen, jonka merkki on pienempi: uudempi vuokra on jo
// käynyt täällä, joten lähettäjän vuokra on varmasti päättynyt.
class Tallennus final : public Solmu<Viesti> {
public:
    explicit Tallennus(bool aitaus) : aitaus_(aitaus) {}

    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        if (aitaus_ && v.merkki < suurin_) {
            y.kirjaa("HYLKAA arvon " + std::to_string(v.arvo) +
                     ": merkki " + std::to_string(v.merkki) + " < " +
                     std::to_string(suurin_));
            y.laheta(lahettaja, {Viesti::Laji::Hylatty});
            return;
        }
        suurin_ = std::max(suurin_, v.merkki);
        arvo = v.arvo;
        y.kirjaa("tallentaa arvon " + std::to_string(v.arvo) +
                 ", merkki " + std::to_string(v.merkki));
        y.laheta(lahettaja, {Viesti::Laji::Ok});
    }

    int arvo = 0;

private:
    bool aitaus_;
    int suurin_ = 0;
};
// @loppu tallennus

// @alku tyontekija
// Työntekijä pyytää vuokran, tarkistaa sen olevan voimassa ja
// kirjoittaa. Tarkistuksen ja kirjoituksen väliin mahtuu tauko
// (roskienkeruu, sivutus, pysäytetty virtuaalikone), jonka aikana
// prosessi ei suorita mitään eikä huomaa ajan kuluvan.
class Tyontekija final : public Solmu<Viesti> {
public:
    Tyontekija(Aika aloitus, Aika tauko, int arvo)
        : aloitus_(aloitus), tauko_(tauko), arvo_(arvo) {}

    void kaynnisty(Yhteys<Viesti>& y) override {
        y.ajasta(aloitus_, PYYDA);
    }

    void ajastin(Yhteys<Viesti>& y, int tunniste) override {
        if (tunniste == PYYDA) {
            y.laheta(LUKKO, {Viesti::Laji::Pyyda});
        } else {   // tauko on ohi: kirjoitus lähtee tarkistamatta
            y.kirjaa("kirjoittaa arvon " + std::to_string(arvo_) +
                     " merkilla " + std::to_string(merkki_));
            y.laheta(TALLENNUS, {Viesti::Laji::Kirjoita, merkki_, arvo_});
        }
    }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Varattu) {
            y.ajasta(100, PYYDA);            // yritetään uudelleen
        } else if (v.laji == Viesti::Laji::Vuokra) {
            merkki_ = v.merkki;
            y.kirjaa(tauko_ == 0 ? "sai vuokran ja tarkisti sen"
                     : "sai vuokran, tarkisti sen ja pysahtyy " +
                           std::to_string(tauko_) + " ms");
            y.ajasta(tauko_, KIRJOITA);
        }
    }

private:
    enum { PYYDA, KIRJOITA };
    Aika aloitus_, tauko_;
    int arvo_, merkki_ = 0;
};
// @loppu tyontekija

// @alku koe
// A saa vuokran ensin ja pysähtyy 400 ms:ksi, kaksi kertaa vuokran
// keston verran. Sillä välin vuokra vanhenee ja B saa uuden.
void koe(const char* nimi, bool aitaus) {
    std::printf("%s\n", nimi);
    Verkkoasetukset a{.viive_min = 1, .viive_max = 5};
    Simulaattori<Viesti> sim(4, 1, a,
        [aitaus](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == LUKKO) return std::make_unique<Lukkopalvelu>();
            if (i == TALLENNUS) return std::make_unique<Tallennus>(aitaus);
            if (i == TYO_A)
                return std::make_unique<Tyontekija>(0, 400, 100);
            return std::make_unique<Tyontekija>(150, 0, 200);   // TYO_B
        });
    sim.tulosta_loki(true);
    sim.aja(1000);
    int arvo = sim.solmu<Tallennus>(TALLENNUS)->arvo;
    std::printf("lopputila: arvo %d (%s)\n\n", arvo,
                arvo == 200 ? "uusimman haltijan"
                            : "vanha haltija ylikirjoitti uuden");
}
// @loppu koe

int main() {
    std::printf("s0 lukkopalvelu, s1 tallennus, s2 tyontekija A,"
                " s3 tyontekija B\n\n");
    koe("ilman aitausta", false);
    koe("aitausmerkilla", true);
}
