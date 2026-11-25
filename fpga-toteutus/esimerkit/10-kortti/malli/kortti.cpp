// Simuloitu iCEBreaker-kortti. Malli ajaa suunnitelman ylintä tasoa
// (kortti_ylin) Verilatorilla ja esittää kortin oheislaitteita:
// kelloa, painikkeita, ledejä, USB-sarjaporttia ja VGA-näyttöä.
//
//   kortti [--kehyksia N] [--kuvat HAKEMISTO]
//          [--vcd TIEDOSTO --alku-us A --vali-us V --naytteita K]
//
// Tuloste on tapahtumaloki, jonka testi vertaa tallennettuun. --kuvat
// tallentaa valitut kehykset PPM-kuvina ja --vcd nastojen tilat
// logiikka-analysaattorin tapaan.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iterator>
#include <memory>
#include <string>
#include <vector>

#include "Vkortti_ylin.h"
#include "verilated.h"

namespace {

// @alku aika
// Malli laskee aikaa pikselikellon jaksoina. PLL on simulaatiossa suora
// kytkentä, joten kellonasta saa suoraan 25,125 MHz.
constexpr uint64_t KELLO_HZ = 25'125'000;
constexpr uint64_t BITTI = 218;          // jaksoa per UART-bitti (115200)

constexpr uint64_t AIKARAJA = 800 * 525;  // jaksoa kehystä kohden

uint64_t jaksoiksi(uint64_t us) { return us * KELLO_HZ / 1'000'000; }
unsigned ms(uint64_t jakso) {
    return static_cast<unsigned>(jakso * 1000 / KELLO_HZ);
}
// @loppu aika

// Tapahtumalokin rivi: aika millisekunteina ja viesti.
void loki(uint64_t jakso, const std::string& viesti) {
    std::printf("[%3u ms] %s\n", ms(jakso), viesti.c_str());
}

// @alku naytto
// Näyttö näkee vain tahdistuspulssit ja värit. Kuvan paikka lasketaan
// pulsseista kuten oikeassa näytössä: tilassa 640 x 480 ensimmäinen
// pikseli tulee 144 jaksoa vaakatahdistuksen alun jälkeen ja ensimmäinen
// rivi 35 riviä pystytahdistuksen alun jälkeen.
class Naytto {
  public:
    static constexpr int LEVEYS = 640, KORKEUS = 480;
    static constexpr int VAAKA_ALKU = 96 + 48, PYSTY_ALKU = 2 + 33;

    // Kutsutaan joka pikselikellolla. Palauttaa true, kun kehys valmistui.
    bool nayte(bool hs, bool vs, unsigned rgb) {
        bool valmis = false;
        if (ed_vs_ && !vs) {                 // pystytahdistus alkaa
            if (kaynnissa_) {
                rivit_yht_ = rivi_;
                ++kehyksia_;
                valmis = true;
            }
            kaynnissa_ = true;
            rivi_ = 0;
            vs_riveja_ = 0;
        }
        if (!ed_vs_ && vs) vs_pituus_ = vs_riveja_;
        if (ed_hs_ && !hs) {                 // vaakatahdistus alkaa
            if (rivi_ > 0) jaksot_yht_ = sarake_ + 1;
            sarake_ = 0;
            ++rivi_;
            if (!vs) ++vs_riveja_;
        } else {
            ++sarake_;
        }
        if (!hs) ++hs_nyt_;
        if (!ed_hs_ && hs) { hs_pituus_ = hs_nyt_; hs_nyt_ = 0; }
        ed_hs_ = hs;
        ed_vs_ = vs;

        const int x = sarake_ - VAAKA_ALKU, y = rivi_ - PYSTY_ALKU;
        if (kaynnissa_ && x >= 0 && x < LEVEYS && y >= 0 && y < KORKEUS)
            kuva_[static_cast<size_t>(y) * LEVEYS + x] =
                static_cast<uint16_t>(rgb);
        else if (kaynnissa_ && rgb != 0)
            ++ulkopuolella_;                 // väriä pimennysaikana
        return valmis;
    }
// @loppu naytto

    // FNV-1a-tarkiste kehyksen pikseleistä.
    uint32_t tarkiste() const {
        uint32_t h = 2166136261u;
        for (uint16_t p : kuva_) {
            h = (h ^ (p & 0xff)) * 16777619u;
            h = (h ^ (p >> 8)) * 16777619u;
        }
        return h;
    }

    // Tallentaa kehyksen PPM-kuvana (neljän bitin värit kahdeksaksi).
    void tallenna(const std::string& polku) const {
        std::FILE* f = std::fopen(polku.c_str(), "wb");
        if (!f) { std::perror(polku.c_str()); std::exit(1); }
        std::fprintf(f, "P6\n%d %d\n255\n", LEVEYS, KORKEUS);
        for (uint16_t p : kuva_) {
            const unsigned char v[3] = {
                static_cast<unsigned char>(((p >> 8) & 15) * 17),
                static_cast<unsigned char>(((p >> 4) & 15) * 17),
                static_cast<unsigned char>((p & 15) * 17)};
            std::fwrite(v, 1, 3, f);
        }
        std::fclose(f);
    }

    int kehyksia() const { return kehyksia_; }

    void yhteenveto() const {
        std::printf("näyttö: rivi %d jaksoa (tahdistus %d), "
                    "kehys %d riviä (tahdistus %d)\n",
                    jaksot_yht_, hs_pituus_, rivit_yht_, vs_pituus_);
        const uint64_t sadasosat =
            KELLO_HZ * 100 / (static_cast<uint64_t>(jaksot_yht_) *
                              static_cast<uint64_t>(rivit_yht_));
        std::printf("näyttö: virkistystaajuus %u,%02u Hz\n",
                    static_cast<unsigned>(sadasosat / 100),
                    static_cast<unsigned>(sadasosat % 100));
        std::printf("näyttö: värillisiä pikseleitä kuva-alueen "
                    "ulkopuolella %ld\n", ulkopuolella_);
    }

  private:
    std::vector<uint16_t> kuva_ =
        std::vector<uint16_t>(static_cast<size_t>(LEVEYS) * KORKEUS);
    bool ed_hs_ = true, ed_vs_ = true, kaynnissa_ = false;
    int sarake_ = 0, rivi_ = 0, hs_nyt_ = 0, vs_riveja_ = 0;
    int jaksot_yht_ = 0, rivit_yht_ = 0, hs_pituus_ = 0, vs_pituus_ = 0;
    int kehyksia_ = 0;
    long ulkopuolella_ = 0;
};

// @alku paate
// Sarjaportin toinen pää: tietokoneen pääteohjelma. Vastaanotto etsii
// aloitusbitin ja näytteistää bitit niiden keskeltä; lähetys siirtää
// tavun linjalle bitti kerrallaan.
class Paate {
  public:
    // Suunnitelman tx-nasta joka jaksolla.
    void vastaanota(uint64_t jakso, bool tx) {
        if (rx_bitti_ < 0) {
            if (!tx) { rx_bitti_ = 0; rx_ajastin_ = BITTI / 2; }
        } else if (rx_ajastin_ > 0) {
            --rx_ajastin_;
        } else {
            rx_ajastin_ = BITTI - 1;
            if (rx_bitti_ >= 1 && rx_bitti_ <= 8)
                rx_tavu_ = (rx_tavu_ >> 1) | (tx ? 0x80u : 0u);
            if (++rx_bitti_ == 10) {
                rx_bitti_ = -1;
                if (rx_tavu_ == '\n') {
                    loki(jakso, "sarjaportti <- \"" + rivi_ + "\"");
                    rivi_.clear();
                } else {
                    rivi_ += static_cast<char>(rx_tavu_);
                }
            }
        }
    }

    void laheta(uint64_t jakso, char merkki) {
        loki(jakso, std::string("sarjaportti -> '") + merkki + "'");
        // Aloitusbitti, kahdeksan databittiä alin ensin, lopetusbitti.
        tx_kehys_ = (1u << 9) | (static_cast<unsigned>(merkki) << 1);
        tx_jaljella_ = 10 * BITTI;
    }

    // Suunnitelman rx-nastan tila tällä jaksolla.
    bool linja() {
        if (tx_jaljella_ == 0) return true;
        const uint64_t bitti = 9 - (tx_jaljella_ - 1) / BITTI;
        --tx_jaljella_;
        return (tx_kehys_ >> bitti) & 1u;
    }
// @loppu paate

  private:
    int rx_bitti_ = -1;
    uint64_t rx_ajastin_ = 0;
    unsigned rx_tavu_ = 0;
    std::string rivi_;
    unsigned tx_kehys_ = 0;
    uint64_t tx_jaljella_ = 0;
};

// @alku painikkeet
// Painike ei sulkeudu siististi: koskettimet pomppivat muutaman
// millisekunnin ajan. Malli tuottaa värähtelyn näennäissatunnaisesti
// kiinteästä siemenestä, joten ajo toistuu samanlaisena.
class Painikkeet {
  public:
    static constexpr uint64_t VARAHTELY_US = 3000;

    void muuta(uint64_t jakso, int painike, bool pohjaan) {
        const uint64_t loppu = jakso + jaksoiksi(VARAHTELY_US);
        bool taso = pohjaan;
        uint64_t t = jakso;
        while (true) {
            muutokset_.push_back({t, painike, taso});
            t += jaksoiksi(100 + satunnainen() % 500);    // 0,1-0,6 ms
            if (t >= loppu) break;
            taso = !taso;
        }
        if (taso != pohjaan) muutokset_.push_back({loppu, painike, pohjaan});
    }

    bool tila(uint64_t jakso, int painike) {
        while (seuraava_ < muutokset_.size() &&
               muutokset_[seuraava_].jakso <= jakso) {
            tasot_[muutokset_[seuraava_].painike] =
                muutokset_[seuraava_].taso;
            ++seuraava_;
        }
        return tasot_[painike];
    }
// @loppu painikkeet

  private:
    struct Muutos { uint64_t jakso; int painike; bool taso; };
    uint32_t satunnainen() {
        siemen_ = siemen_ * 1664525u + 1013904223u;
        return siemen_ >> 8;
    }
    std::vector<Muutos> muutokset_;
    size_t seuraava_ = 0;
    bool tasot_[4] = {false, false, false, false};
    uint32_t siemen_ = 2024;
};

// @alku analysaattori
// Logiikka-analysaattori: tallentaa kortin nastat tasavälein
// VCD-tiedostoon, jonka voi avata aaltomuotokatselimessa. Näytekello
// "nayte" nousee jokaisen näytteen kohdalla.
class Analysaattori {
  public:
    Analysaattori(const std::string& polku, uint64_t alku_us,
                  uint64_t vali_us, unsigned naytteita)
        : f_(std::fopen(polku.c_str(), "w")), alku_us_(alku_us),
          vali_us_(vali_us), naytteita_(naytteita) {
        if (!f_) { std::perror(polku.c_str()); std::exit(1); }
        std::fprintf(f_, "$timescale 1us $end\n$scope module kortti $end\n");
        std::fprintf(f_, "$var wire 1 ! nayte $end\n");
        for (size_t i = 0; i < NIMET.size(); ++i)
            std::fprintf(f_, "$var wire 1 %c %s $end\n",
                         static_cast<char>('a' + i), NIMET[i]);
        std::fprintf(f_, "$upscope $end\n$enddefinitions $end\n#0\n0!\n");
    }
    ~Analysaattori() { std::fclose(f_); }

    // bitit: nastojen tilat samassa järjestyksessä kuin NIMET.
    void nayte(uint64_t jakso, unsigned bitit) {
        if (otettu_ >= naytteita_) return;
        const uint64_t us = alku_us_ + otettu_ * vali_us_;
        if (jakso < jaksoiksi(us)) return;
        std::fprintf(f_, "#%llu\n", static_cast<unsigned long long>(us));
        for (size_t i = 0; i < NIMET.size(); ++i) {
            const unsigned b = (bitit >> i) & 1u;
            if (otettu_ == 0 || b != ((ed_ >> i) & 1u))
                std::fprintf(f_, "%u%c\n", b, static_cast<char>('a' + i));
        }
        std::fprintf(f_, "1!\n#%llu\n0!\n",
                     static_cast<unsigned long long>(us + vali_us_ / 2));
        ed_ = bitit;
        ++otettu_;
    }
// @loppu analysaattori

  private:
    static constexpr std::array<const char*, 10> NIMET = {
        "btn1", "btn2", "btn3", "led1", "led2", "led3", "led4", "led5",
        "rx", "tx"};
    std::FILE* f_;
    uint64_t alku_us_, vali_us_;
    unsigned naytteita_, otettu_ = 0, ed_ = 0;
};

// @alku skenaario
// Käyttäjän toimet: aika millisekunteina, toimi ja kohde.
enum class Toimi { Paina, Vapauta, Merkki };
struct Tapahtuma { unsigned ms; Toimi toimi; int kohde; };
const Tapahtuma SKENAARIO[] = {
    {40, Toimi::Paina, 1},    {90, Toimi::Vapauta, 1},
    {140, Toimi::Paina, 1},   {180, Toimi::Vapauta, 1},
    {200, Toimi::Merkki, '3'},
    {260, Toimi::Paina, 2},   {300, Toimi::Vapauta, 2},
    {330, Toimi::Merkki, 'x'},
    {380, Toimi::Paina, 1},   {420, Toimi::Vapauta, 1},
    {460, Toimi::Paina, 3},
};
// Kehykset, joiden tarkiste tulostetaan ja jotka --kuvat tallentaa.
const int TALLENNETTAVAT[] = {2, 14, 26};
// @loppu skenaario

std::string ledit(unsigned led) {
    std::string s = "ledit ";
    for (int i = 0; i < 4; ++i) s += (led >> i) & 1u ? '#' : '.';
    s += ' ';
    s += (led >> 4) & 1u ? '#' : '.';
    return s;
}

}  // namespace

int main(int argc, char** argv) {
    int kehyksia = 30;
    std::string kuvat, vcd;
    uint64_t alku_us = 0, vali_us = 1000;
    unsigned naytteita = 0;
    for (int i = 1; i + 1 < argc; i += 2) {
        const std::string valinta = argv[i];
        const char* arvo = argv[i + 1];
        if (valinta == "--kehyksia") kehyksia = std::atoi(arvo);
        else if (valinta == "--kuvat") kuvat = arvo;
        else if (valinta == "--vcd") vcd = arvo;
        else if (valinta == "--alku-us") alku_us = std::strtoull(arvo, 0, 10);
        else if (valinta == "--vali-us") vali_us = std::strtoull(arvo, 0, 10);
        else if (valinta == "--naytteita")
            naytteita = static_cast<unsigned>(std::atoi(arvo));
        else { std::fprintf(stderr, "tuntematon valinta %s\n", argv[i]);
               return 2; }
    }

    const auto konteksti = std::make_unique<VerilatedContext>();
    const auto kortti = std::make_unique<Vkortti_ylin>(konteksti.get());
    Naytto naytto;
    Paate paate;
    Painikkeet painikkeet;
    std::unique_ptr<Analysaattori> analysaattori;
    if (!vcd.empty())
        analysaattori = std::make_unique<Analysaattori>(
            vcd, alku_us, vali_us, naytteita);

    size_t tapahtuma = 0;
    unsigned ed_ledit = ~0u;
    uint32_t ed_tarkiste = 0;
    bool samat = false;

    // Valmis kehys: valituista kehyksistä tarkiste lokiin ja kuva
    // tiedostoon. Kahden viimeisen kehyksen tarkisteita verrataan.
    const auto kehys_valmis = [&](uint64_t jakso) {
        const int n = naytto.kehyksia();
        const uint32_t tarkiste = naytto.tarkiste();
        if (std::find(std::begin(TALLENNETTAVAT),
                      std::end(TALLENNETTAVAT), n) !=
            std::end(TALLENNETTAVAT)) {
            char rivi[64];
            std::snprintf(rivi, sizeof rivi,
                          "näyttö: kehys %d, tarkiste %08x", n, tarkiste);
            loki(jakso, rivi);
            if (!kuvat.empty()) {
                char nimi[32];
                std::snprintf(nimi, sizeof nimi, "/kehys-%02d.ppm", n);
                naytto.tallenna(kuvat + nimi);
            }
        }
        samat = tarkiste == ed_tarkiste;
        ed_tarkiste = tarkiste;
    };

// @alku silmukka
    for (uint64_t jakso = 0; naytto.kehyksia() < kehyksia; ++jakso) {
        if (jakso > AIKARAJA * static_cast<uint64_t>(kehyksia + 2)) {
            std::fprintf(stderr, "aikaraja: näyttö ei saa kehyksiä\n");
            return 1;
        }
        // Käyttäjän toimet tällä jaksolla.
        while (tapahtuma < std::size(SKENAARIO) &&
               jaksoiksi(SKENAARIO[tapahtuma].ms * 1000ull) <= jakso) {
            const Tapahtuma& t = SKENAARIO[tapahtuma++];
            if (t.toimi == Toimi::Merkki) {
                paate.laheta(jakso, static_cast<char>(t.kohde));
            } else {
                const bool pohjaan = t.toimi == Toimi::Paina;
                painikkeet.muuta(jakso, t.kohde, pohjaan);
                loki(jakso, "painike " + std::to_string(t.kohde) +
                            (pohjaan ? " painetaan" : " vapautetaan"));
            }
        }
        // Tulot ja kellon nouseva reuna.
        kortti->btn1 = painikkeet.tila(jakso, 1);
        kortti->btn2 = painikkeet.tila(jakso, 2);
        kortti->btn3 = painikkeet.tila(jakso, 3);
        kortti->rx = paate.linja();
        kortti->clk_12 = 1;
        kortti->eval();

        // Oheislaitteet lukevat lähdöt.
        const unsigned led = kortti->led1 | kortti->led2 << 1 |
            kortti->led3 << 2 | kortti->led4 << 3 | kortti->led5 << 4;
        if (led != ed_ledit) loki(jakso, ledit(led));
        ed_ledit = led;
        paate.vastaanota(jakso, kortti->tx);
        const unsigned rgb = static_cast<unsigned>(
            kortti->vga_r << 8 | kortti->vga_g << 4 | kortti->vga_b);
        if (naytto.nayte(kortti->vga_hs, kortti->vga_vs, rgb))
            kehys_valmis(jakso);
        if (analysaattori)
            analysaattori->nayte(
                jakso, static_cast<unsigned>(
                           kortti->btn1 | kortti->btn2 << 1 |
                           kortti->btn3 << 2 | led << 3 |
                           kortti->rx << 8 | kortti->tx << 9));

        kortti->clk_12 = 0;
        kortti->eval();
    }
// @loppu silmukka

    std::printf("kehyksiä %d\n", naytto.kehyksia());
    naytto.yhteenveto();
    std::printf("kaksi viimeistä kehystä samat (pallo pysäytetty): %s\n",
                samat ? "kyllä" : "ei");
    kortti->final();
    return 0;
}
