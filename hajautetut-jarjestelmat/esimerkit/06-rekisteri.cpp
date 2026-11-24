// Replikoitu rekisteri kolmella toteutuksella ja niiden historioiden
// linearisoituvuus: yksi kopio, kvoorumi ilman takaisinkirjoitusta ja
// ABD-algoritmi (Attiya, Bar-Noy ja Dolev 1995), jossa luku kirjoittaa
// näkemänsä arvon kvoorumille ennen vastaamista.
#include <cstdio>
#include <memory>
#include <utility>
#include <vector>

#include "yhteinen/historia.hpp"
#include "yhteinen/simulaattori.hpp"

using Leima = std::pair<int, int>;   // (versio, asiakas)

struct Viesti {
    enum class Laji { Kysy, Tila, Kirjoita, Ok } laji;
    int pyynto;
    Leima leima;
    int arvo;
};

// @alku replika
class Replika final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        if (v.laji == Viesti::Laji::Kysy) {
            y.laheta(lahettaja, {Viesti::Laji::Tila, v.pyynto, leima_,
                                 arvo_});
        } else if (v.laji == Viesti::Laji::Kirjoita) {
            if (leima_ < v.leima) {
                leima_ = v.leima;
                arvo_ = v.arvo;
            }
            y.laheta(lahettaja, {Viesti::Laji::Ok, v.pyynto, {}, 0});
        }
    }
private:
    Leima leima_{0, 0};
    int arvo_ = 0;
};
// @loppu replika

struct Asetus {
    std::vector<int> replikat;
    int kvoorumi;
    bool takaisinkirjoitus;
};

// @alku asiakas
// Operaatio etenee kahdessa vaiheessa. Ensin kysytään kvoorumilta
// suurin leima. Kirjoitus kirjoittaa sitten uuden arvon suuremmalla
// leimalla; ABD-luku kirjoittaa näkemänsä arvon takaisin. Ilman
// takaisinkirjoitusta luku palaa heti ensimmäisen vaiheen jälkeen.
class Asiakas final : public Solmu<Viesti> {
public:
    Asiakas(Asetus a, std::vector<Operaatio>& h) : a_(std::move(a)), h_(h) {}
    void kaynnisty(Yhteys<Viesti>& y) override { y.ajasta(1, 0); }

    void ajastin(Yhteys<Viesti>& y, int t) override {
        if (t > 0) {                      // aikakatkaisu
            if (t != opnro_ || vaihe_ == 0) return;
            if (kirjoitus_) h_.push_back(op_);     // tulos tuntematon
            vaihe_ = 0;
        }
        if (y.kello() > 600) return;
        ++opnro_;
        y.ajasta(300, opnro_);
        kirjoitus_ = y.satunnainen().tapahtuu(400);
        op_ = {y.oma(), kirjoitus_, 0, y.kello(), KESKEN};
        if (kirjoitus_) op_.arvo = y.oma() * 100 + ++kirjoituksia_;
        vaihe_ = 1;
        laheta(y, {Viesti::Laji::Kysy, 0, {}, 0});
    }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (vaihe_ == 0 || v.pyynto != pyynto_ ||
            ++vastauksia_ > a_.kvoorumi)
            return;
        if (vaihe_ == 1 && paras_ < v.leima) {
            paras_ = v.leima;
            arvo_ = v.arvo;
        }
        if (vastauksia_ < a_.kvoorumi) return;
        if (vaihe_ == 1 && (kirjoitus_ || a_.takaisinkirjoitus)) {
            vaihe_ = 2;
            Leima l = paras_;
            int arvo = arvo_;
            if (kirjoitus_) {
                l = {paras_.first + 1, y.oma()};
                arvo = op_.arvo;
            }
            laheta(y, {Viesti::Laji::Kirjoita, 0, l, arvo});
            return;
        }
        if (!kirjoitus_) op_.arvo = arvo_;
        op_.loppu = y.kello();
        h_.push_back(op_);
        vaihe_ = 0;
        y.ajasta(y.satunnainen().valilta(1, 20), 0);
    }

private:
    void laheta(Yhteys<Viesti>& y, Viesti v) {
        v.pyynto = ++pyynto_;
        vastauksia_ = 0;
        if (v.laji == Viesti::Laji::Kysy) paras_ = {-1, -1};
        for (int r : a_.replikat) y.laheta(r, v);
    }
    Asetus a_;
    std::vector<Operaatio>& h_;
    Operaatio op_{};
    bool kirjoitus_ = false;
    int vaihe_ = 0, opnro_ = 0, pyynto_ = 0, vastauksia_ = 0;
    int kirjoituksia_ = 0;
    Leima paras_{-1, -1};
    int arvo_ = 0;
};
// @loppu asiakas

// @alku koe
struct Tulos {
    int virheita = 0, ensimmainen = 0;
};

Tulos virheelliset(const Asetus& a, int ajoja) {
    Tulos t;
    for (int s = 1; s <= ajoja; ++s) {
        std::vector<Operaatio> h;
        Verkkoasetukset va{.viive_min = 1, .viive_max = 40,
                           .katoaa = 200};
        Simulaattori<Viesti> sim(6, static_cast<std::uint64_t>(s), va,
            [&](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
                if (i < 3) return std::make_unique<Replika>();
                return std::make_unique<Asiakas>(a, h);
            });
        sim.aja(2000);
        if (!linearisoituva(h) && ++t.virheita == 1) t.ensimmainen = s;
    }
    return t;
}
// @loppu koe

int main() {
    const int AJOJA = 200;
    std::printf("toteutus                    ei-linearisoituvia  "
                "ensimmainen siemen\n");
    struct Rivi {
        const char* nimi;
        Asetus a;
    };
    for (const Rivi& r : {Rivi{"yksi kopio", {{0}, 1, false}},
                          Rivi{"kvoorumi ilman takaisinkirj.",
                               {{0, 1, 2}, 2, false}},
                          Rivi{"ABD", {{0, 1, 2}, 2, true}}}) {
        Tulos t = virheelliset(r.a, AJOJA);
        std::printf("%-28s %8d / %d  %18d\n", r.nimi, t.virheita, AJOJA,
                    t.ensimmainen);
    }
}
