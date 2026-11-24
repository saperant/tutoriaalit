// Kuormien karakterisointi: neljä laskentaydintä, jotka laskevat oikean
// tuloksen ja kirjaavat samalla jokaisen muistiviittauksen jälkeen ja
// operaatioluokkien määrät.
//
// Käyttö:  ohjelma HAKEMISTO   kirjoittaa jäljet HAKEMISTO/<ydin>.txt
//
// Instrumentointi on käsin tehty malli siitä, mitä käännetty koodi
// tekee. Oikeat työkalut (Pin, DynamoRIO, Valgrind, gem5) saavat samat
// tiedot ajamalla käännettyä ohjelmaa.
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// @alku laskuri
// Dynaamiset operaatiot luokittain, kuten käskyjakaumassa.
struct Laskuri {
    std::uint64_t lataukset = 0, tallennukset = 0;
    std::uint64_t liukuluku = 0, kokonaisluku = 0, haarat = 0;

    std::uint64_t yhteensa() const {
        return lataukset + tallennukset + liukuluku + kokonaisluku +
               haarat;
    }
    // Silmukan kierroksen hallinta: indeksin kasvatus ja ehtohaara.
    void kierros() {
        ++kokonaisluku;
        ++haarat;
    }
};
// @loppu laskuri

// @alku jalki
// Kirjaa viittaukset tiedostoon ja laskuriin.
class Jalki {
public:
    Jalki(const std::filesystem::path& polku, Laskuri& laskuri)
        : tiedosto_(polku), laskuri_(laskuri) {
        if (!tiedosto_) {
            throw std::runtime_error("ei voi kirjoittaa: " + polku.string());
        }
    }
    void luku(std::uint64_t osoite) {
        ++laskuri_.lataukset;
        kirjaa('R', osoite);
    }
    void kirjoitus(std::uint64_t osoite) {
        ++laskuri_.tallennukset;
        kirjaa('W', osoite);
    }

private:
    void kirjaa(char tyyppi, std::uint64_t osoite) {
        char rivi[32];
        const int n = std::snprintf(rivi, sizeof rivi, "%c %llx\n", tyyppi,
                                    static_cast<unsigned long long>(osoite));
        tiedosto_.write(rivi, n);
    }
    std::ofstream tiedosto_;
    Laskuri& laskuri_;
};

// Taulukko, jonka alkiot sijaitsevat mallin osoiteavaruudessa. Osoitteet
// jaetaan sivun rajalta, jotta jälki ei riipu ajokerran osoitteista.
template <typename T>
class Taulukko {
public:
    Taulukko(Jalki& jalki, std::uint64_t& seuraava, std::size_t koko)
        : jalki_(jalki), alku_(seuraava), data_(koko) {
        seuraava += (koko * sizeof(T) + 4095) / 4096 * 4096;
    }
    T lue(std::size_t i) const {
        jalki_.luku(alku_ + i * sizeof(T));
        return data_.at(i);
    }
    void kirjoita(std::size_t i, T arvo) {
        jalki_.kirjoitus(alku_ + i * sizeof(T));
        data_.at(i) = arvo;
    }
    // Alustus ilman kirjausta (tulee ennen mitattavaa osuutta).
    T& alusta(std::size_t i) { return data_.at(i); }

private:
    Jalki& jalki_;
    std::uint64_t alku_;
    std::vector<T> data_;
};
// @loppu jalki

// Kiinteän siemenen satunnaisluvut (xorshift64), jotta jälki on sama
// kaikilla kääntäjillä ja koneilla.
class Satunnainen {
public:
    explicit Satunnainen(std::uint64_t siemen) : tila_(siemen) {}
    std::uint64_t seuraava() {
        tila_ ^= tila_ << 13;
        tila_ ^= tila_ >> 7;
        tila_ ^= tila_ << 17;
        return tila_;
    }

private:
    std::uint64_t tila_;
};

constexpr std::uint64_t ALKU = 0x10000;

// @alku virta
// a[i] = b[i] + s * c[i] kahdesti.
double virta(Jalki& j, Laskuri& l) {
    constexpr std::size_t N = 2048;
    std::uint64_t osoite = ALKU;
    Taulukko<double> a(j, osoite, N), b(j, osoite, N), c(j, osoite, N);
    for (std::size_t i = 0; i < N; ++i) {
        b.alusta(i) = static_cast<double>(i % 7);
        c.alusta(i) = static_cast<double>(i % 5);
    }
    const double s = 0.5;
    for (int kierros = 0; kierros < 2; ++kierros) {
        for (std::size_t i = 0; i < N; ++i) {
            l.kierros();
            a.kirjoita(i, b.lue(i) + s * c.lue(i));
            l.liukuluku += 2;
        }
    }
    double summa = 0;
    for (std::size_t i = 0; i < N; ++i) summa += a.alusta(i);
    return summa;
}
// @loppu virta

// C = A * B, n x n, rivijärjestys. Naiivi ijk-järjestys lukee B:tä
// sarakkeittain; lohkottu käsittelee L x L -lohkoja.
constexpr std::size_t MN = 32;

struct Matriisit {
    std::uint64_t osoite = ALKU;
    Taulukko<double> a, b, c;
    Matriisit(Jalki& j)
        : a(j, osoite, MN * MN), b(j, osoite, MN * MN),
          c(j, osoite, MN * MN) {
        for (std::size_t i = 0; i < MN * MN; ++i) {
            a.alusta(i) = static_cast<double>(i % 11) - 5;
            b.alusta(i) = static_cast<double>(i % 13) - 6;
        }
    }
    double summa() {
        double s = 0;
        for (std::size_t i = 0; i < MN * MN; ++i) s += c.alusta(i);
        return s;
    }
};

double naiivi(Jalki& j, Laskuri& l) {
    Matriisit m(j);
    for (std::size_t i = 0; i < MN; ++i) {
        for (std::size_t k = 0; k < MN; ++k) {
            l.kierros();
            double s = 0;
            for (std::size_t x = 0; x < MN; ++x) {
                l.kierros();
                s += m.a.lue(i * MN + x) * m.b.lue(x * MN + k);
                l.liukuluku += 2;
            }
            m.c.kirjoita(i * MN + k, s);
        }
    }
    return m.summa();
}

// @alku lohkottu
double lohkottu(Jalki& j, Laskuri& l) {
    constexpr std::size_t L = 8;
    Matriisit m(j);
    for (std::size_t ii = 0; ii < MN; ii += L) {
        for (std::size_t kk = 0; kk < MN; kk += L) {
            for (std::size_t xx = 0; xx < MN; xx += L) {
                for (std::size_t i = ii; i < ii + L; ++i) {
                    for (std::size_t k = kk; k < kk + L; ++k) {
                        l.kierros();
                        double s = xx == 0 ? 0 : m.c.lue(i * MN + k);
                        for (std::size_t x = xx; x < xx + L; ++x) {
                            l.kierros();
                            s += m.a.lue(i * MN + x) * m.b.lue(x * MN + k);
                            l.liukuluku += 2;
                        }
                        m.c.kirjoita(i * MN + k, s);
                    }
                }
            }
        }
    }
    return m.summa();
}
// @loppu lohkottu

// @alku lista
// Linkitetty lista 1024 solmusta (64 tavua), solmut satunnaisessa
// järjestyksessä muistissa. Seuraava osoite selviää vasta latauksesta.
double lista(Jalki& j, Laskuri& l) {
    constexpr std::size_t N = 1024;
    std::uint64_t osoite = ALKU;
    Taulukko<std::uint64_t> seuraava(j, osoite, N * 8);  // 8 sanaa/solmu
    std::vector<std::size_t> jarjestys(N);
    for (std::size_t i = 0; i < N; ++i) jarjestys[i] = i;
    Satunnainen sat(2026);
    for (std::size_t i = N - 1; i > 0; --i) {  // Fisher-Yates
        std::swap(jarjestys[i], jarjestys[sat.seuraava() % (i + 1)]);
    }
    for (std::size_t i = 0; i < N; ++i) {
        seuraava.alusta(jarjestys[i] * 8) = jarjestys[(i + 1) % N];
        seuraava.alusta(jarjestys[i] * 8 + 1) = i;  // solmun arvo
    }
    double summa = 0;
    std::size_t solmu = jarjestys[0];
    for (std::size_t askel = 0; askel < 4 * N; ++askel) {
        l.kierros();
        summa += static_cast<double>(seuraava.lue(solmu * 8 + 1));
        ++l.liukuluku;
        solmu = seuraava.lue(solmu * 8);
    }
    return summa;
}
// @loppu lista

// @alku main
int main(int argc, char** argv) {
    const std::filesystem::path hakemisto = argc > 1 ? argv[1] : ".";
    std::filesystem::create_directories(hakemisto);
    using Ydin = double (*)(Jalki&, Laskuri&);
    const std::vector<std::pair<std::string, Ydin>> ytimet = {
        {"virta", virta}, {"naiivi", naiivi},
        {"lohkottu", lohkottu}, {"lista", lista}};
    std::ofstream laskurit(hakemisto / "laskurit.txt");
    std::printf("%-9s %8s %6s %6s %6s %6s %6s %6s\n", "ydin", "operaat",
                "lat%", "tal%", "liuku%", "kok%", "haara%", "FLOP/B");
    for (const auto& [nimi, ydin] : ytimet) {
        Laskuri l;
        Jalki j(hakemisto / (nimi + ".txt"), l);
        const double tulos = ydin(j, l);
        const double n = static_cast<double>(l.yhteensa());
        const auto osuus = [n](std::uint64_t x) {
            return 100.0 * static_cast<double>(x) / n;
        };
        const double tavut = 8.0 * static_cast<double>(l.lataukset +
                                                       l.tallennukset);
        std::printf("%-9s %8llu %6.1f %6.1f %6.1f %6.1f %6.1f %6.3f"
                    "   tulos %.0f\n",
                    nimi.c_str(), static_cast<unsigned long long>(n),
                    osuus(l.lataukset), osuus(l.tallennukset),
                    osuus(l.liukuluku), osuus(l.kokonaisluku),
                    osuus(l.haarat),
                    static_cast<double>(l.liukuluku) / tavut, tulos);
        laskurit << nimi << ' ' << l.lataukset << ' ' << l.tallennukset
                 << ' ' << l.liukuluku << ' ' << l.kokonaisluku << ' '
                 << l.haarat << '\n';
    }
}
// @loppu main
