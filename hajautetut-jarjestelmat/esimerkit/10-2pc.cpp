// Kaksivaiheinen sitoutuminen (2PC) yhdellä koordinaattorilla ja
// kolmella osallistujalla. Kun koordinaattori kaatuu äänestyksen ja
// päätöksen välissä, osallistujat jäävät epätietoisiksi ja pitävät
// lukkojaan, kunnes koordinaattori palaa ja lukee lokinsa.
#include <algorithm>
#include <cstdio>
#include <memory>
#include <string>

#include "yhteinen/simulaattori.hpp"

struct Viesti {
    enum class Laji { Valmistele, Aani, Paatos, Kysy } laji;
    bool kylla = false;
};

// @alku levy
// Pysyvä loki. Koordinaattori kirjaa transaktion alun ja päätöksen,
// osallistuja valmistelunsa ja päätöksen.
struct Levy {
    bool aloitettu = false, valmisteltu = false;
    int paatos = -1;             // -1 ei päätöstä, 0 peru, 1 sitouta
};
// @loppu levy

// @alku koordinaattori
// Päätöksen kirjaaminen ja lähettäminen ovat omia tapahtumiaan, jotta
// testi voi kaataa koordinaattorin niiden väliin.
class Koordinaattori final : public Solmu<Viesti> {
public:
    enum { ALOITA, KIRJAA, LAHETA };
    explicit Koordinaattori(Levy& l) : levy_(l) {}

    void kaynnisty(Yhteys<Viesti>& y) override {
        if (levy_.paatos >= 0) {
            y.ajasta(0, LAHETA);           // palautuminen: lähetä uudelleen
        } else if (levy_.aloitettu) {
            levy_.paatos = 0;              // ei päätöstä lokissa: peru
            y.ajasta(0, LAHETA);
        } else {
            y.ajasta(10, ALOITA);
        }
    }

    void ajastin(Yhteys<Viesti>& y, int t) override {
        if (t == ALOITA) {
            levy_.aloitettu = true;
            for (int s = 1; s <= 3; ++s)
                y.laheta(s, {Viesti::Laji::Valmistele});
        } else if (t == KIRJAA) {
            levy_.paatos = kyllat == 3 ? 1 : 0;   // päätös on nyt pysyvä
            y.ajasta(0, LAHETA);
        } else {
            for (int s = 1; s <= 3; ++s)
                y.laheta(s, {Viesti::Laji::Paatos, levy_.paatos == 1});
            lahetetty = true;
        }
    }

    void vastaanota(Yhteys<Viesti>& y, int l, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Kysy) {
            if (levy_.paatos >= 0)
                y.laheta(l, {Viesti::Laji::Paatos, levy_.paatos == 1});
        } else if (v.laji == Viesti::Laji::Aani && levy_.paatos < 0 &&
                   !paattamassa_) {
            if (v.kylla) ++kyllat;
            if (!v.kylla || kyllat == 3) {
                paattamassa_ = true;
                y.ajasta(0, KIRJAA);
            }
        }
    }

    int kyllat = 0;
    bool lahetetty = false;
private:
    Levy& levy_;
    bool paattamassa_ = false;
};
// @loppu koordinaattori

// @alku osallistuja
// Äänestää kyllä, lukitsee resurssin ja kirjaa valmistelun. Jos päätöstä
// ei kuulu, osallistuja kysyy sitä koordinaattorilta 100 ms välein:
// kyllä-äänen jälkeen se ei saa päättää yksin.
class Osallistuja final : public Solmu<Viesti> {
public:
    Osallistuja(Levy& l, bool kylla) : levy_(l), kylla_(kylla) {}

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Valmistele) {
            if (kylla_) {
                levy_.valmisteltu = true;
                lukittu = y.kello();
                y.ajasta(100, 0);
            } else {
                levy_.paatos = 0;               // voi perua heti itse
            }
            y.laheta(0, {Viesti::Laji::Aani, kylla_});
        } else if (v.laji == Viesti::Laji::Paatos && levy_.paatos < 0) {
            levy_.paatos = v.kylla ? 1 : 0;
            vapautettu = y.kello();
        }
    }
    void ajastin(Yhteys<Viesti>& y, int) override {
        if (levy_.paatos >= 0) return;
        ++kyselyja;
        y.laheta(0, {Viesti::Laji::Kysy});
        y.ajasta(100, 0);
    }
    Aika lukittu = -1, vapautettu = -1;
    int kyselyja = 0;
private:
    Levy& levy_;
    bool kylla_;
};
// @loppu osallistuja

// @alku koe
// kaatuu: 0 ei kaadu, 1 kaatuu kaikkien äänten jälkeen ennen päätöksen
// kirjaamista, 2 kaatuu kirjaamisen jälkeen ennen lähettämistä.
void koe(const char* nimi, bool kaikki_kylla, int kaatuu) {
    Simulaattori<Viesti, Levy> sim(4, 1, {.viive_min = 1, .viive_max = 10},
        [&](int i, Levy& l) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == 0) return std::make_unique<Koordinaattori>(l);
            return std::make_unique<Osallistuja>(l, kaikki_kylla || i != 3);
        });
    bool kaatunut = false;
    sim.jokaisen_jalkeen([&] {
        auto* k = sim.solmu<Koordinaattori>(0);
        if (!k || kaatunut || k->lahetetty) return;
        bool kohta1 = k->kyllat == 3 && sim.levy(0).paatos < 0;
        bool kohta2 = sim.levy(0).paatos >= 0;
        if ((kaatuu == 1 && kohta1) || (kaatuu == 2 && kohta2)) {
            kaatunut = true;
            sim.kaada(0);
            sim.kun(sim.nyt() + 1000, [&] { sim.kaynnista(0); });
        }
    });
    sim.aja(3000);
    std::string tulos;
    Aika lukko = 0;
    int kyselyja = 0;
    for (int s = 1; s <= 3; ++s) {
        int p = sim.levy(s).paatos;
        tulos += p == 1 ? 'S' : p == 0 ? 'P' : '?';
        auto* o = sim.solmu<Osallistuja>(s);
        if (o->lukittu >= 0)
            lukko = std::max(lukko, o->vapautettu - o->lukittu);
        kyselyja += o->kyselyja;
    }
    std::printf("%-40s %s  %8lld  %8d\n", nimi, tulos.c_str(),
                static_cast<long long>(lukko), kyselyja);
}
// @loppu koe

int main() {
    std::printf("tilanne                                  paat.  "
                "lukko ms  kyselyja\n");
    koe("kaikki kylla", true, 0);
    koe("osallistuja 3 sanoo ei", false, 0);
    koe("koordinaattori kaatuu ennen paatosta", true, 1);
    koe("koordinaattori kaatuu paatoksen jalkeen", true, 2);
}
