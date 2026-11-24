// CAP ja PACELC simulaattorissa. Kolme replikaa ja kaksi asiakasta;
// verkko jaetaan hetkellä 1000 kahtia: {r0, r1, asiakas A} ja
// {r2, asiakas B}. CP-tila vaatii enemmistön kuittauksen, AP-tila
// kuittaa paikallisesti ja levittää muutokset myöhemmin joko
// "viimeinen kirjoitus voittaa" -säännöllä tai yhdistämällä (CRDT).
#include <cstdio>
#include <memory>
#include <set>

#include "yhteinen/simulaattori.hpp"

enum class Tila { CP, ApLww, ApCrdt };

struct Viesti {
    enum class Laji { Lisaa, Ok, Tila } laji;
    int pyynto = 0, alkio = 0;
    std::set<int> alkiot{};
    Aika leima = 0;
    int replika = 0;
};

constexpr int A = 3, B = 4;

// @alku replika
class Replika final : public Solmu<Viesti> {
public:
    explicit Replika(Tila t) : tila_(t) {}
    void kaynnisty(Yhteys<Viesti>& y) override {
        if (tila_ != Tila::CP) y.ajasta(50, 0);
    }
    void vastaanota(Yhteys<Viesti>& y, int l, const Viesti& v) override {
        if (v.laji == Viesti::Laji::Lisaa) {
            alkiot.insert(v.alkio);
            leima_ = y.kello();
            y.laheta(l, {.laji = Viesti::Laji::Ok, .pyynto = v.pyynto});
        } else if (v.laji == Viesti::Laji::Tila) {
            if (tila_ == Tila::ApCrdt) {
                alkiot.insert(v.alkiot.begin(), v.alkiot.end());
            } else if (v.leima > leima_ ||
                       (v.leima == leima_ && v.replika > y.oma())) {
                alkiot = v.alkiot;              // koko arvo korvataan
                leima_ = v.leima;
            }
        }
    }
    void ajastin(Yhteys<Viesti>& y, int) override {   // levitys
        for (int r = 0; r < 3; ++r)
            if (r != y.oma())
                y.laheta(r, {.laji = Viesti::Laji::Tila, .alkiot = alkiot,
                             .leima = leima_, .replika = y.oma()});
        y.ajasta(50, 0);
    }
    std::set<int> alkiot;
private:
    Tila tila_;
    Aika leima_ = -1;
};
// @loppu replika

// @alku asiakas
// Lisää uuden alkion, odottaa vastausta ja jatkaa 20 ms:n päästä.
// CP-tilassa pyyntö menee kaikille ja vaatii kaksi kuittausta,
// AP-tilassa vain lähimmälle replikalle. Pyyntö epäonnistuu, jos
// kuittauksia ei ole tullut 300 ms:ssa.
class Asiakas final : public Solmu<Viesti> {
public:
    Asiakas(Tila t, int lahin) : tila_(t), lahin_(lahin) {}
    void kaynnisty(Yhteys<Viesti>& y) override { y.ajasta(20, -1); }

    void ajastin(Yhteys<Viesti>& y, int t) override {
        if (t >= 0) {                                 // aikakatkaisu
            if (t == pyynto_ && !valmis_) kirjaa(y, false);
            return;
        }
        if (!valmis_) return;
        if (y.kello() >= 3000) return;
        ++pyynto_;
        valmis_ = false;
        kuittauksia_ = 0;
        alku_ = y.kello();
        int alkio = y.oma() * 10000 + pyynto_;
        if (tila_ == Tila::CP) {
            for (int r = 0; r < 3; ++r)
                y.laheta(r, {.laji = Viesti::Laji::Lisaa, .pyynto = pyynto_,
                             .alkio = alkio});
        } else {
            y.laheta(lahin_, {.laji = Viesti::Laji::Lisaa,
                              .pyynto = pyynto_, .alkio = alkio});
        }
        viimeisin_ = alkio;
        y.ajasta(300, pyynto_);
    }

    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.pyynto != pyynto_ || valmis_) return;
        if (tila_ != Tila::CP || ++kuittauksia_ == 2) kirjaa(y, true);
    }

    int onnistui_jaossa = 0, yrityksia_jaossa = 0;
    Aika viive = 0;
    int viiveita = 0;
    std::set<int> kuitatut;
private:
    void kirjaa(Yhteys<Viesti>& y, bool ok) {
        valmis_ = true;
        bool jaossa = alku_ >= 1000 && alku_ < 2000;
        if (jaossa) {
            ++yrityksia_jaossa;
            onnistui_jaossa += ok;
        } else if (ok) {
            viive += y.kello() - alku_;
            ++viiveita;
        }
        if (ok) kuitatut.insert(viimeisin_);
        y.ajasta(20, -1);
    }
    Tila tila_;
    int lahin_, pyynto_ = 0, kuittauksia_ = 0, viimeisin_ = 0;
    bool valmis_ = true;
    Aika alku_ = 0;
};
// @loppu asiakas

// @alku koe
void koe(const char* nimi, Tila tila) {
    Verkkoasetukset a{.viive_min = 5, .viive_max = 15};
    Simulaattori<Viesti> sim(5, 1, a,
        [tila](int i, Tyhja&) -> std::unique_ptr<Solmu<Viesti>> {
            if (i == A) return std::make_unique<Asiakas>(tila, 0);
            if (i == B) return std::make_unique<Asiakas>(tila, 2);
            return std::make_unique<Replika>(tila);
        });
    // Kaksi konesalia: {r0, r1, A} ja {r2, B}; niiden välillä +40 ms.
    auto sali = [](int i) { return i == 2 || i == B; };
    sim.lisaviive([sali](int x, int y) {
        return sali(x) != sali(y) ? 40 : 0;
    });
    sim.kun(1000, [&] { sim.jaa({{0, 1, A}, {2, B}}); });
    sim.kun(2000, [&] { sim.paranna(); });
    sim.aja(4000);
    auto* a0 = sim.solmu<Asiakas>(A);
    auto* b0 = sim.solmu<Asiakas>(B);
    const auto& lopuksi = sim.solmu<Replika>(0)->alkiot;
    int kadonnut = 0;
    for (auto* as : {a0, b0})
        for (int x : as->kuitatut) kadonnut += !lopuksi.contains(x);
    std::printf("%-8s %5d/%-3d %5d/%-3d %6lld %6lld  %8d\n", nimi,
                a0->onnistui_jaossa, a0->yrityksia_jaossa,
                b0->onnistui_jaossa, b0->yrityksia_jaossa,
                static_cast<long long>(a0->viive / a0->viiveita),
                static_cast<long long>(b0->viive / b0->viiveita),
                kadonnut);
}
// @loppu koe

int main() {
    std::printf("         onnistui jaon aikana  viive ilman jakoa  "
                "kuitattu\n");
    std::printf("tila       A (enem.) B (vahem.)     A ms   B ms  mutta "
                "kadonnut\n");
    koe("CP", Tila::CP);
    koe("AP-LWW", Tila::ApLww);
    koe("AP-CRDT", Tila::ApCrdt);
}
