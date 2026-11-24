// FIR-suotimen bittileveyksien vertailu liukulukuviitteeseen.
#define SC_INCLUDE_FX
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <systemc>

#include "fir.hpp"

// Merkkien (ei tavujen) määrä UTF-8:ssa tulosteen tasaamiseen.
static int merkkeja(const std::string& s) {
    return static_cast<int>(std::count_if(
        s.begin(), s.end(), [](char c) { return (c & 0xC0) != 0x80; }));
}

// @alku vertailu
// Virhe ilmoitetaan ulostulon vähiten merkitsevinä bitteinä
// (LSB = 2^-15). Viitteen tulos rajataan Q1.15:n alueelle, koska
// kyllästys on toteutuksen määritelty ominaisuus eikä virhe.
struct Tulos {
    double suurin = 0.0, signaali = 0.0, kohina = 0.0;
};

template <typename Malli, typename Signaali>
Tulos aja(Signaali signaali) {
    Malli malli;
    fir::Viite viite;
    const double lsb = std::ldexp(1.0, -15);
    Tulos t;
    for (int n = 0; n < 2000; ++n) {
        const fir::Nayte x = signaali(n);
        const double y = malli.suodata(x).to_double();
        const double yv =
            std::clamp(viite.suodata(x.to_double()), -1.0, 1.0 - lsb);
        t.suurin = std::max(t.suurin, std::fabs(y - yv) / lsb);
        t.signaali += yv * yv;
        t.kohina += (y - yv) * (y - yv);
    }
    return t;
}

template <typename Malli>
void vertaa(const std::string& nimi) {
    // Hidas ja nopea sini; suodin vaimentaa nopean.
    const Tulos sini = aja<Malli>([](int n) {
        return 0.6 * std::sin(0.01 * n) + 0.35 * std::sin(2.9 * n);
    });
    // Pahin tapaus: näytteiden etumerkit samat kuin kertoimien, jolloin
    // välisummat kasvavat suurimmiksi.
    const Tulos pahin = aja<Malli>([](int n) {
        return fir::KERTOIMET[7 - n % 8] < 0 ? -0.95 : 0.95;
    });
    std::printf("%s%*s %6.2f %6.1f %9.2f\n", nimi.c_str(),
                26 - merkkeja(nimi), "",
                sini.suurin, 10.0 * std::log10(sini.signaali / sini.kohina),
                pahin.suurin);
}
// @loppu vertailu

int sc_main(int, char*[]) {
    // @alku main
    using sc_dt::sc_fixed;
    using sc_dt::SC_RND;
    using sc_dt::SC_TRN;
    using sc_dt::SC_WRAP;
    std::printf("%-26s %6s %6s %9s\n", "toteutus", "LSB", "SNR dB",
                "pahin LSB");
    vertaa<fir::Suodin<>>("tarkat välitulokset");
    // Tulot katkaistaan tai pyöristetään 18 bittiin ennen summausta.
    vertaa<fir::Suodin<sc_fixed<18, 2, SC_TRN>>>("tulot 18 b, katkaisu");
    vertaa<fir::Suodin<sc_fixed<18, 2, SC_RND>>>("tulot 18 b, pyöristys");
    // Summaimesta puuttuvat suojabitit: välisumma kiertää.
    vertaa<fir::Suodin<fir::TarkkaTulo, sc_fixed<32, 1, SC_TRN, SC_WRAP>>>(
        "summa ilman suojabittejä");
    // @loppu main
    return 0;
}
