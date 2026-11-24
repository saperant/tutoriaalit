// Tilisiirrot häviävän verkon yli. Ilman uudelleenyritystä siirtoja
// katoaa, uudelleenyrityksellä osa tehdään kahdesti. Idempotenssiavain
// tekee toistosta vaarattoman, mutta vain jos käsitellyt avaimet
// säilyvät palvelimen kaatumisen yli.
#include <cstdio>
#include <memory>
#include <set>

#include "yhteinen/simulaattori.hpp"

struct Viesti {
    bool kuittaus;
    int avain;
};

enum class Tapa { Kerran, Uudelleen, AvainMuistissa, AvainLevylla };

// @alku palvelin
struct Levy {
    long siirretty = 0;          // tehtyjen siirtojen määrä
    std::set<int> kasitellyt;    // pysyvä idempotenssitaulu
};

class Pankki final : public Solmu<Viesti> {
public:
    Pankki(Tapa t, Levy& l) : tapa_(t), levy_(l) {}
    void vastaanota(Yhteys<Viesti>& y, int l, const Viesti& v) override {
        bool tehty = false;
        if (tapa_ == Tapa::AvainLevylla)
            tehty = !levy_.kasitellyt.insert(v.avain).second;
        else if (tapa_ == Tapa::AvainMuistissa)
            tehty = !muisti_.insert(v.avain).second;
        if (!tehty) ++levy_.siirretty;       // siirto ja avain samassa
        y.laheta(l, {true, v.avain});        // transaktiossa
    }
private:
    Tapa tapa_;
    Levy& levy_;
    std::set<int> muisti_;                   // katoaa kaatuessa
};
// @loppu palvelin

// @alku asiakas
// Lähettää 50 siirtoa peräkkäin. Uudelleenyrittävä asiakas lähettää
// saman avaimen uudelleen, kunnes kuittaus tulee.
class Asiakas final : public Solmu<Viesti> {
public:
    explicit Asiakas(Tapa t) : tapa_(t) {}
    void kaynnisty(Yhteys<Viesti>& y) override { seuraava(y); }
    void vastaanota(Yhteys<Viesti>& y, int, const Viesti& v) override {
        if (v.avain != avain_ || valmis_) return;
        valmis_ = true;
        ++kuitatut;
        seuraava(y);
    }
    void ajastin(Yhteys<Viesti>& y, int t) override {
        if (t != avain_ || valmis_) return;
        if (tapa_ == Tapa::Kerran) return seuraava(y);   // luovutetaan
        laheta(y);
    }
    int kuitatut = 0;
private:
    void seuraava(Yhteys<Viesti>& y) {
        if (avain_ == 50) return;
        ++avain_;
        valmis_ = false;
        laheta(y);
    }
    void laheta(Yhteys<Viesti>& y) {
        y.laheta(1, {false, avain_});
        y.ajasta(40, avain_);
    }
    Tapa tapa_;
    int avain_ = 0;
    bool valmis_ = true;
};
// @loppu asiakas

int main() {
    std::printf("tapa               tehty / 50  kuitattu\n");
    const char* nimet[] = {"kerran", "uudelleen", "avain muistissa",
                           "avain levylla"};
    for (int t = 0; t < 4; ++t) {
        Tapa tapa = static_cast<Tapa>(t);
        Verkkoasetukset a{.viive_min = 1, .viive_max = 20, .katoaa = 150,
                          .monistuu = 50};
        Simulaattori<Viesti, Levy> sim(2, 3, a,
            [tapa](int i, Levy& l) -> std::unique_ptr<Solmu<Viesti>> {
                if (i == 0) return std::make_unique<Asiakas>(tapa);
                return std::make_unique<Pankki>(tapa, l);
            });
        for (Aika k = 200; k <= 2000; k += 200) {   // pankki kaatuu usein
            sim.kun(k, [&] { sim.kaada(1); });
            sim.kun(k + 30, [&] { sim.kaynnista(1); });
        }
        sim.aja(5000);
        std::printf("%-18s %10ld  %8d\n", nimet[t], sim.levy(1).siirretty,
                    sim.solmu<Asiakas>(0)->kuitatut);
    }
}
