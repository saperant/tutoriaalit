// mittari.hpp: kello, toistomittaus ja mittauksen esto-optimoinnit.
//
// Esimerkit toimivat kahdessa tilassa. Ilman argumentteja ne ajavat
// toiminnallisen testin ja tulostavat vain deterministisiä tuloksia.
// Argumentilla --mittaa ne mittaavat ajan optimoidulla käännöksellä,
// ja argumentilla --kerran ne ajavat yhden tavan Valgrindia varten
// (ks. Makefile).
#ifndef MITTARI_HPP
#define MITTARI_HPP

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <span>
#include <string_view>
#include <vector>

namespace mittari {

// @alku pida
// Pakottaa arvon olemaan olemassa: tyhjä asm-lause "lukee" arvon, eikä
// kääntäjä voi poistaa sen laskentaa. Käskyjä ei synny.
template <typename T>
inline void pida(const T& arvo)
{
    asm volatile("" : : "r,m"(arvo) : "memory");
}

// Tekee arvosta kääntäjälle tuntemattoman: asm-lause voisi muuttaa
// sitä, joten kääntäjä ei voi laskea sen varassa mitään etukäteen.
template <typename T>
inline void piilota(T& arvo)
{
    asm volatile("" : "+m"(arvo) : : "memory");
}

// Kertoo kääntäjälle, että mikä tahansa muisti on voinut muuttua:
// arvoja ei saa pitää rekistereissä tämän kohdan yli.
inline void sotke_muisti()
{
    asm volatile("" : : : "memory");
}
// @loppu pida

struct Tilasto {
    double mediaani_ms;
    double mad_ms;      // mediaanin absoluuttinen poikkeama
};

inline double mediaani(std::vector<double> x)
{
    std::ranges::sort(x);
    std::size_t n = x.size();
    return n % 2 ? x[n / 2] : (x[n / 2 - 1] + x[n / 2]) / 2.0;
}

// @alku mittaa
// Ajaa funktion kerran lämmittelyksi ja sitten `toistot` kertaa.
// Palauttaa kestojen mediaanin ja hajonnan millisekunteina.
template <typename F>
Tilasto mittaa(F&& f, int toistot)
{
    using Kello = std::chrono::steady_clock;
    std::vector<double> naytteet;
    naytteet.reserve(static_cast<std::size_t>(toistot));
    f();
    for (int i = 0; i < toistot; ++i) {
        auto alku = Kello::now();
        f();
        std::chrono::duration<double, std::milli> d = Kello::now() - alku;
        naytteet.push_back(d.count());
    }
    double m = mediaani(naytteet);
    for (double& x : naytteet) {
        x = std::abs(x - m);
    }
    return {m, mediaani(naytteet)};
}
// @loppu mittaa

// @alku kalibroi
// Google Benchmarkin tapaan: toistomäärä kaksinkertaistetaan, kunnes
// yksi mittaus kestää vähintään 20 ms, jolloin kellon tarkkuus ja
// kutsun hinta eivät vääristä tulosta. Palauttaa nanosekunnit toistoa
// kohden.
template <typename F>
double ns_per_toisto(F&& f)
{
    using Kello = std::chrono::steady_clock;
    long toistot = 1;
    while (true) {
        auto alku = Kello::now();
        for (long i = 0; i < toistot; ++i) {
            f();
        }
        std::chrono::duration<double, std::nano> d = Kello::now() - alku;
        if (d.count() > 20e6) {
            return d.count() / static_cast<double>(toistot);
        }
        toistot *= 2;
    }
}
// @loppu kalibroi

// Tulostaa mittausrivin ja suhteen vertailuaikaan, jos se on annettu.
inline void tulosta(std::string_view nimi, Tilasto t, double vertailu = 0)
{
    std::printf("  %-26.*s %9.3f ms +-%7.3f", static_cast<int>(nimi.size()),
                nimi.data(), t.mediaani_ms, t.mad_ms);
    if (vertailu > 0 && t.mediaani_ms > 0) {
        double s = vertailu / t.mediaani_ms;
        if (s > 0.95 && s < 1.05) {
            std::printf("  yhta nopea");
        } else if (s >= 1) {
            std::printf("  %.1f x nopeampi", s);
        } else {
            std::printf("  %.1f x hitaampi", 1 / s);
        }
    }
    std::printf("\n");
}

// Ohjelman tila komentoriviltä: testi, --mittaa tai --kerran TAPA N.
struct Tila {
    bool mittaa = false;
    std::string_view kerran;     // tyhjä, jos ei Valgrind-ajoa
    long n = 0;
};

inline Tila lue_tila(std::span<char*> argv)
{
    Tila t;
    if (argv.size() > 1 && std::string_view{argv[1]} == "--mittaa") {
        t.mittaa = true;
    } else if (argv.size() > 3 && std::string_view{argv[1]} == "--kerran") {
        t.kerran = argv[2];
        t.n = std::strtol(argv[3], nullptr, 10);
    }
    return t;
}

}  // namespace mittari

#endif
