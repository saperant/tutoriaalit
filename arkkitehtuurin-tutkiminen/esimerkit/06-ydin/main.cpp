// Yksityiskohtainen ydinmalli: epäjärjestyksessä suorittava ydin, jonka
// ikkuna (ROB) on W käskyä ja leveys D käskyä jaksossa, sekä
// välimuistimalli. Ohjelma on synteettinen ja vaiheittainen: laskentaa,
// virtaavaa muistiliikennettä ja osoitinjahtia.
//
// Tulostaa kunkin ikkunakoon jaksot ja kirjoittaa työhakemistoon:
//   kaskyt.txt       käskyvirta merkkeinä intervallimallille (luku 6)
//   intervallit.txt  joka 1000 käskyn intervallin jaksot ja
//                    peruslohkovektori (W = 64) SimPointia varten
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <list>
#include <vector>

// @alku kasky
enum class Tyyppi : char {
    Alu = 'a', Osuma = 'l', Huti = 'm', RiippuvaHuti = 'd',
    Haara = 'b', VaaraHaara = 'x'
};

struct Kasky {
    Tyyppi tyyppi;
    int riippuu = -1;  // edeltävän käskyn indeksi tai -1
    int lohko = 0;     // peruslohko, johon käsky kuuluu
};
// @loppu kasky

class Satunnainen {
public:
    explicit Satunnainen(std::uint64_t siemen) : tila_(siemen) {}
    std::uint64_t seuraava() {
        tila_ ^= tila_ << 13;
        tila_ ^= tila_ >> 7;
        tila_ ^= tila_ << 17;
        return tila_;
    }
    bool todennakoisyys(double p) {
        return static_cast<double>(seuraava() % 1000000) < p * 1e6;
    }

private:
    std::uint64_t tila_;
};

// @alku valimuisti
// 8 KiB, 4-tie, LRU, 64 tavun rivit.
class Valimuisti {
public:
    bool osuu(std::uint64_t osoite) {
        const std::uint64_t rivi = osoite / 64;
        auto& joukko = joukot_[rivi % joukot_.size()];
        const auto it = std::find(joukko.begin(), joukko.end(), rivi);
        const bool osui = it != joukko.end();
        if (osui) {
            joukko.erase(it);
        } else if (joukko.size() == 4) {
            joukko.pop_back();
        }
        joukko.push_front(rivi);
        return osui;
    }

private:
    std::array<std::list<std::uint64_t>, 32> joukot_;
};
// @loppu valimuisti

// @alku ohjelma
// Kolme vaihetyyppiä, kullakin kaksi peruslohkoa (lohkot 0-5).
//   0 laskenta: pieni taulukko (osumia), vaikeasti ennustettavat haarat
//   1 virta:    peräkkäiset lataukset suuresta taulukosta, toisistaan
//               riippumattomia
//   2 jahti:    linkitetty lista (lohko 4), jokainen lataus riippuu
//               edellisestä
constexpr int INTERVALLI = 1000, INTERVALLEJA = 100;

std::vector<Kasky> tee_ohjelma() {
    Satunnainen sat(42);
    Valimuisti vm;
    std::vector<Kasky> ohjelma;
    std::uint64_t virta = 1 << 20;
    int edellinen_lataus = -1;
    while (ohjelma.size() < INTERVALLI * INTERVALLEJA) {
        const int vaihe = static_cast<int>(sat.seuraava() % 3);
        const std::size_t loppu = ohjelma.size() +
            INTERVALLI * (1 + sat.seuraava() % 4);  // 1-4 intervallia
        while (ohjelma.size() < loppu &&
               ohjelma.size() < INTERVALLI * INTERVALLEJA) {
            const int lohko = 2 * vaihe + static_cast<int>(
                sat.seuraava() % 2);
            const int pituus = 8 + 2 * (lohko % 2);
            for (int i = 0; i < pituus - 1; ++i) {
                const int n = static_cast<int>(ohjelma.size());
                Kasky k{Tyyppi::Alu, -1, lohko};
                if (vaihe == 0 && i % 4 == 1) {
                    vm.osuu(0x1000 + 8 * (sat.seuraava() % 256));
                    k.tyyppi = Tyyppi::Osuma;
                } else if (vaihe == 1 && i % 2 == 0) {
                    virta += 8;
                    k.tyyppi = vm.osuu(virta) ? Tyyppi::Osuma : Tyyppi::Huti;
                } else if (lohko == 4 && i == 0) {
                    const std::uint64_t osoite =
                        (2 << 20) + 64 * (sat.seuraava() % 65536);
                    k.tyyppi = vm.osuu(osoite) ? Tyyppi::Osuma
                                               : Tyyppi::RiippuvaHuti;
                    k.riippuu = edellinen_lataus;
                    edellinen_lataus = n;
                } else if (i > 0) {
                    k.riippuu = n - 1;  // aritmetiikkaketju
                }
                ohjelma.push_back(k);
            }
            const double vaara = vaihe == 0 ? 0.15 : 0.01;
            ohjelma.push_back({sat.todennakoisyys(vaara) ? Tyyppi::VaaraHaara
                                                         : Tyyppi::Haara,
                               static_cast<int>(ohjelma.size()) - 1, lohko});
        }
    }
    ohjelma.resize(INTERVALLI * INTERVALLEJA);
    return ohjelma;
}
// @loppu ohjelma

// @alku ajoitus
// Käskykohtainen ajoitus: rajattomasti suoritusyksiköitä, joten käsky
// alkaa heti, kun se on ikkunassa ja sen operandi on valmis. Sääntöjen
// suora laskeminen antaa saman tuloksen kuin jaksoittain etenevä
// simulointi, mutta ajassa O(N).
constexpr long OSUMA = 3, HUTI = 100, PALAUTUS = 8;

std::vector<long> ajoita(const std::vector<Kasky>& ohjelma, int ikkuna,
                         int leveys) {
    const std::size_t n = ohjelma.size();
    std::vector<long> sisaan(n), valmis(n), poistuu(n);
    long uudelleenohjaus = 0;  // väärin ennustetun haaran jälkeen
    for (std::size_t i = 0; i < n; ++i) {
        const Kasky& k = ohjelma[i];
        long t = uudelleenohjaus;
        if (i >= static_cast<std::size_t>(leveys)) {
            t = std::max(t, sisaan[i - leveys] + 1);
        }
        if (i >= static_cast<std::size_t>(ikkuna)) {
            t = std::max(t, poistuu[i - ikkuna]);  // ROB täynnä
        }
        sisaan[i] = t;
        long alku = t;
        if (k.riippuu >= 0) alku = std::max(alku, valmis[k.riippuu]);
        long viive = 1;
        if (k.tyyppi == Tyyppi::Osuma) viive = OSUMA;
        if (k.tyyppi == Tyyppi::Huti || k.tyyppi == Tyyppi::RiippuvaHuti) {
            viive = HUTI;
        }
        valmis[i] = alku + viive;
        if (k.tyyppi == Tyyppi::VaaraHaara) {
            uudelleenohjaus = valmis[i] + PALAUTUS;
        }
        long p = valmis[i];
        if (i > 0) p = std::max(p, poistuu[i - 1]);
        if (i >= static_cast<std::size_t>(leveys)) {
            p = std::max(p, poistuu[i - leveys] + 1);
        }
        poistuu[i] = p;
    }
    return poistuu;
}
// @loppu ajoitus

int main() {
    const std::vector<Kasky> ohjelma = tee_ohjelma();
    std::ofstream kaskyt("kaskyt.txt");
    std::array<int, 6> maarat{};
    for (const Kasky& k : ohjelma) {
        kaskyt.put(static_cast<char>(k.tyyppi));
        ++maarat[std::size_t(k.lohko)];
    }
    kaskyt.put('\n');

    // @alku tulokset
    // Ihanteellinen ajo: ei hutia eikä väärin ennustettua haaraa.
    std::vector<Kasky> ihanne = ohjelma;
    for (Kasky& k : ihanne) {
        if (k.tyyppi == Tyyppi::Huti || k.tyyppi == Tyyppi::RiippuvaHuti) {
            k.tyyppi = Tyyppi::Osuma;
        } else if (k.tyyppi == Tyyppi::VaaraHaara) {
            k.tyyppi = Tyyppi::Haara;
        }
    }
    std::printf("käskyjä %zu, leveys 4\n", ohjelma.size());
    std::printf("%6s %9s %6s %6s\n", "ikkuna", "jaksot", "CPI", "ihanne");
    for (const int ikkuna : {16, 64, 128}) {
        const std::vector<long> poistuu = ajoita(ohjelma, ikkuna, 4);
        const long jaksot = poistuu.back() + 1;
        const long perus = ajoita(ihanne, ikkuna, 4).back() + 1;
        const auto n = static_cast<double>(ohjelma.size());
        std::printf("%6d %9ld %6.3f %6.3f\n", ikkuna, jaksot,
                    static_cast<double>(jaksot) / n,
                    static_cast<double>(perus) / n);
        if (ikkuna != 64) continue;
        std::ofstream intervallit("intervallit.txt");
        long edellinen = 0;
        for (int v = 0; v < INTERVALLEJA; ++v) {
            const long loppu = poistuu[(v + 1) * INTERVALLI - 1] + 1;
            std::array<int, 6> bbv{};
            for (int i = v * INTERVALLI; i < (v + 1) * INTERVALLI; ++i) {
                ++bbv[std::size_t(ohjelma[std::size_t(i)].lohko)];
            }
            intervallit << loppu - edellinen;
            for (const int b : bbv) intervallit << ' ' << b;
            intervallit << '\n';
            edellinen = loppu;
        }
    }
    // @loppu tulokset
    std::printf("käskyjä lohkoittain:");
    for (const int m : maarat) std::printf(" %d", m);
    std::printf("\n");
}
