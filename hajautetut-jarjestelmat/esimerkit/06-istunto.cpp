// Istuntotakuut asynkronisesti replikoidussa järjestelmässä: lue omat
// kirjoituksesi ja monotoniset luvut. Asiakas kirjoittaa johtajalle ja
// lukee satunnaiselta seuraajalta, joka voi olla jäljessä.
// Istuntotunniste (pienin hyväksyttävä versio) korjaa molemmat.
#include <algorithm>
#include <cstdio>
#include <memory>

#include "yhteinen/simulaattori.hpp"

struct Viesti {
    enum class Laji { Kirjoita, Kirjoitettu, Paivita, Lue, Luettu,
                      Jaljessa } laji;
    int versio;       // kirjoitettu, luettu tai vaadittu versio
};

constexpr int JOHTAJA = 0, ASIAKAS = 3;

// @alku replikat
class Johtaja final : public Solmu<Viesti> {
public:
    void kaynnisty(Yhteys<Viesti>& y) override { y.ajasta(50, 0); }
    void vastaanota(Yhteys<Viesti>& y, int l, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Kirjoita)
            y.laheta(l, {Viesti::Laji::Kirjoitettu, ++versio_});
        else if (v.laji == Viesti::Laji::Lue)
            y.laheta(l, {Viesti::Laji::Luettu, versio_});
    }
    void ajastin(Yhteys<Viesti>& y, int) override {   // eräreplikointi
        for (int s : {1, 2}) y.laheta(s, {Viesti::Laji::Paivita, versio_});
        y.ajasta(50, 0);
    }
private:
    int versio_ = 0;
};

class Seuraaja final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int l, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Paivita) {
            versio_ = std::max(versio_, v.versio);
        } else if (v.laji == Viesti::Laji::Lue) {
            if (versio_ >= v.versio)
                y.laheta(l, {Viesti::Laji::Luettu, versio_});
            else
                y.laheta(l, {Viesti::Laji::Jaljessa, versio_});
        }
    }
private:
    int versio_ = 0;
};
// @loppu replikat

struct Laskurit {
    int luvut = 0, omat_hukassa = 0, taaksepain = 0, johtajalta = 0;
};

// @alku asiakas
// Kirjoittaa ja lukee sitten kolme kertaa. Istuntotunnisteella asiakas
// vaatii, että luku on vähintään yhtä tuore kuin mikään, minkä istunto
// on jo kirjoittanut tai lukenut; jäljessä oleva seuraaja kieltäytyy,
// ja asiakas lukee johtajalta.
class Asiakas final : public Solmu<Viesti> {
public:
    Asiakas(bool tunniste, Laskurit& l) : tunniste_(tunniste), l_(l) {}
    void kaynnisty(Yhteys<Viesti>& y) override { kirjoita(y); }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        switch (v.laji) {
        case Viesti::Laji::Kirjoitettu:
            kirjoitettu_ = v.versio;
            lukuja_ = 0;
            lue(y, static_cast<int>(y.satunnainen().valilta(1, 2)));
            break;
        case Viesti::Laji::Jaljessa:
            ++l_.johtajalta;
            lue(y, JOHTAJA);
            break;
        case Viesti::Laji::Luettu:
            ++l_.luvut;
            if (v.versio < kirjoitettu_) ++l_.omat_hukassa;
            if (v.versio < luettu_) ++l_.taaksepain;
            luettu_ = std::max(luettu_, v.versio);
            if (++lukuja_ < 3)
                lue(y, static_cast<int>(y.satunnainen().valilta(1, 2)));
            else if (y.kello() < 3000)
                kirjoita(y);
            break;
        default:
            break;
        }
    }
private:
    void kirjoita(Yhteys<Viesti>& y) {
        y.laheta(JOHTAJA, {Viesti::Laji::Kirjoita, 0});
    }
    void lue(Yhteys<Viesti>& y, int kohde) {
        int vaatimus = tunniste_ ? std::max(kirjoitettu_, luettu_) : 0;
        y.laheta(kohde, {Viesti::Laji::Lue, vaatimus});
    }
    bool tunniste_;
    Laskurit& l_;
    int kirjoitettu_ = 0, luettu_ = 0, lukuja_ = 0;
};
// @loppu asiakas

int main() {
    std::printf("tapa             luvut  omat hukassa  taaksepain  "
                "johtajalta\n");
    for (bool tunniste : {false, true}) {
        Laskurit l;
        for (std::uint64_t s = 1; s <= 10; ++s) {
            Verkkoasetukset a{.viive_min = 1, .viive_max = 20};
            Simulaattori<Viesti> sim(4, s, a,
                [&](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
                    if (i == JOHTAJA) return std::make_unique<Johtaja>();
                    if (i == ASIAKAS)
                        return std::make_unique<Asiakas>(tunniste, l);
                    return std::make_unique<Seuraaja>();
                });
            sim.aja(4000);
        }
        std::printf("%-15s %6d  %12d  %10d  %10d\n",
                    tunniste ? "istuntotunniste" : "ei takuita", l.luvut,
                    l.omat_hukassa, l.taaksepain, l.johtajalta);
    }
}
