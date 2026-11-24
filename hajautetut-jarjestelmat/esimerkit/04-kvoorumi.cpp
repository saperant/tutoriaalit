// Johtajaton replikointi kvoorumeilla: N = 3 replikaa, kirjoitus
// odottaa W kuittausta ja luku R vastausta. Kun R + W > N, luku- ja
// kirjoituskvoorumi leikkaavat, eikä luku palauta vanhempaa arvoa kuin
// ennen sen alkua valmistunut kirjoitus. Lukukorjaus päivittää jälkeen
// jääneet replikat.
#include <algorithm>
#include <cstdio>
#include <memory>
#include <vector>

#include "yhteinen/simulaattori.hpp"

constexpr int N = 3, KIRJOITTAJA = 3, LUKIJA = 4;

struct Viesti {
    enum class Laji { Kirjoita, KirjoitusOk, Lue, Luettu } laji;
    int pyynto;
    int versio;
};

// @alku replika
class Replika final : public Solmu<Viesti> {
public:
    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        if (v.laji == Viesti::Laji::Kirjoita) {
            versio = std::max(versio, v.versio);
            y.laheta(lahettaja, {Viesti::Laji::KirjoitusOk, v.pyynto, 0});
        } else if (v.laji == Viesti::Laji::Lue) {
            y.laheta(lahettaja, {Viesti::Laji::Luettu, v.pyynto, versio});
        }
    }
    int versio = 0;
};
// @loppu replika

struct Havainnot {
    int valmis = 0;            // viimeisin valmistunut kirjoitus
    long luvut = 0, vanhentuneet = 0;
    Aika lukuviive = 0, kirjoitusviive = 0;
    long kirjoitukset = 0;
};

// @alku kirjoittaja
// Kirjoittaa versiot 1, 2, 3, ... peräkkäin. Kirjoitus on valmis, kun
// W replikaa on kuitannut; kuittauksen puuttuessa lähetetään uudelleen.
class Kirjoittaja final : public Solmu<Viesti> {
public:
    Kirjoittaja(int w, Havainnot& h) : w_(w), h_(h) {}
    void kaynnisty(Yhteys<Viesti>& y) override { aloita(y); }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.pyynto != versio_ || ++kuittauksia_ != w_) return;
        h_.valmis = versio_;
        h_.kirjoitusviive += y.kello() - alku_;
        ++h_.kirjoitukset;
        if (y.kello() < 2000) y.ajasta(10, -1);
    }
    void ajastin(Yhteys<Viesti>& y, int t) override {
        if (t == -1) aloita(y);
        else if (t == versio_ && kuittauksia_ < w_) laheta(y);
    }
private:
    void aloita(Yhteys<Viesti>& y) {
        ++versio_;
        kuittauksia_ = 0;
        alku_ = y.kello();
        laheta(y);
    }
    void laheta(Yhteys<Viesti>& y) {
        for (int r = 0; r < N; ++r)
            y.laheta(r, {Viesti::Laji::Kirjoita, versio_, versio_});
        y.ajasta(100, versio_);
    }
    int w_;
    Havainnot& h_;
    int versio_ = 0, kuittauksia_ = 0;
    Aika alku_ = 0;
};
// @loppu kirjoittaja

// @alku lukija
// Lukee jatkuvasti. Luku on vanhentunut, jos se palauttaa vanhemman
// version kuin ennen luvun alkua valmistunut kirjoitus.
class Lukija final : public Solmu<Viesti> {
public:
    Lukija(int r, bool korjaa, Havainnot& h)
        : r_(r), korjaa_(korjaa), h_(h) {}
    void kaynnisty(Yhteys<Viesti>& y) override { aloita(y); }

    void vastaanota(Yhteys<Viesti>& y, int lahettaja,
                    const Viesti& v) override {
        if (v.laji != Viesti::Laji::Luettu || v.pyynto != pyynto_ ||
            vastauksia_ >= r_)
            return;
        vastanneet_.push_back({lahettaja, v.versio});
        if (++vastauksia_ < r_) return;
        int paras = 0;
        for (auto [s, ver] : vastanneet_) paras = std::max(paras, ver);
        ++h_.luvut;
        if (paras < raja_) ++h_.vanhentuneet;
        h_.lukuviive += y.kello() - alku_;
        if (korjaa_)                                 // lukukorjaus
            for (auto [s, ver] : vastanneet_)
                if (ver < paras)
                    y.laheta(s, {Viesti::Laji::Kirjoita, -1, paras});
        y.ajasta(y.satunnainen().valilta(1, 15), -1);
    }
    void ajastin(Yhteys<Viesti>& y, int t) override {
        if (t == -1 || (t == pyynto_ && vastauksia_ < r_)) aloita(y);
    }
private:
    void aloita(Yhteys<Viesti>& y) {
        if (y.kello() > 3000) return;
        ++pyynto_;
        vastauksia_ = 0;
        vastanneet_.clear();
        raja_ = h_.valmis;
        alku_ = y.kello();
        for (int r = 0; r < N; ++r)
            y.laheta(r, {Viesti::Laji::Lue, pyynto_, 0});
        y.ajasta(100, pyynto_);                      // aikakatkaisu
    }
    struct Vastaus {
        int solmu, versio;
    };
    int r_;
    bool korjaa_;
    Havainnot& h_;
    int pyynto_ = 0, vastauksia_ = 0, raja_ = 0;
    Aika alku_ = 0;
    std::vector<Vastaus> vastanneet_;
};
// @loppu lukija

// @alku koe
struct Tulos {
    Havainnot h;
    int jaljessa;   // replikoita, joilta puuttuu viimeisin versio lopussa
};

Tulos koe(int r, int w, bool korjaa, int katoaa, std::uint64_t siemen) {
    Havainnot h;
    Verkkoasetukset a{.viive_min = 1, .viive_max = 30, .katoaa = katoaa};
    Simulaattori<Viesti> sim(5, siemen, a,
        [&](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == KIRJOITTAJA)
                return std::make_unique<Kirjoittaja>(w, h);
            if (i == LUKIJA)
                return std::make_unique<Lukija>(r, korjaa, h);
            return std::make_unique<Replika>();
        });
    sim.aja(3500);
    int jaljessa = 0;
    for (int i = 0; i < N; ++i)
        if (sim.solmu<Replika>(i)->versio < h.valmis) ++jaljessa;
    return {h, jaljessa};
}
// @loppu koe

int main() {
    std::printf("N = 3, 10 %% viesteista katoaa, 10 ajoa kutakin\n");
    std::printf(" R  W  R+W>N  vanhentuneet  lukuviive  kirjoitusviive\n");
    for (auto [r, w] : {std::pair{1, 1}, {1, 2}, {2, 2}, {1, 3}, {3, 1}}) {
        long luvut = 0, vanhat = 0, kirj = 0;
        Aika lv = 0, kv = 0;
        for (std::uint64_t s = 1; s <= 10; ++s) {
            Havainnot h = koe(r, w, false, 100, s).h;
            luvut += h.luvut;
            vanhat += h.vanhentuneet;
            lv += h.lukuviive;
            kv += h.kirjoitusviive;
            kirj += h.kirjoitukset;
        }
        std::printf("%2d %2d  %-5s  %10.1f %%  %6lld ms  %11lld ms\n", r,
                    w, r + w > N ? "kylla" : "ei",
                    100.0 * static_cast<double>(vanhat) /
                        static_cast<double>(luvut),
                    static_cast<long long>(lv / luvut),
                    static_cast<long long>(kv / kirj));
    }

    std::printf("\nlukukorjaus, R = W = 2\n");
    for (bool korjaa : {false, true}) {
        int jaljessa = 0;
        for (std::uint64_t s = 1; s <= 10; ++s)
            jaljessa += koe(2, 2, korjaa, 100, s).jaljessa;
        std::printf("%-12s jaljessa olevia replikoita lopussa: %d / 30\n",
                    korjaa ? "korjaus" : "ei korjausta", jaljessa);
    }
}
