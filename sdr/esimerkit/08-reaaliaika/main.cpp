// Lohkoittainen kanavanvalinta ja FM-ilmaisu C++:lla.
//
//   ohjelma                  itsetesti (lohkokoon vaikutus, aanen taso)
//   ohjelma --suodin F       cu8 stdin -> float32-MPX stdout, kanava F Hz
//   ohjelma --mittaa         lapaisy synteettisella signaalilla
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <numbers>
#include <span>
#include <string_view>
#include <vector>

#include "lohkot.hpp"

namespace {

constexpr double kFs = 912e3;
constexpr std::size_t kDesimointi = 4;
constexpr double kPoikkeama = 75e3;

// @alku ketju
// Vastaanotinketju yhdessa oliossa; tila sailyy lohkojen valilla.
class Ketju {
public:
    explicit Ketju(double kanava_hz)
        : nco_(kanava_hz, kFs),
          fir_(sdr::alipaasto(129, 100e3, kFs), kDesimointi),
          ilmaisin_(kFs / kDesimointi, kPoikkeama) {}

    void kasittele(std::span<sdr::Nayte> lohko, std::vector<float>& mpx) {
        valilla_.clear();
        nco_.sekoita(lohko);
        fir_.suodata(lohko, valilla_);
        ilmaisin_.ilmaise(valilla_, mpx);
    }

private:
    sdr::Nco nco_;
    sdr::FirDesimoija fir_;
    sdr::FmIlmaisin ilmaisin_;
    std::vector<sdr::Nayte> valilla_;   // varataan kerran, ei joka lohko
};
// @loppu ketju

// FM-moduloitu 1 kHz:n aani 200 kHz:n kohdalla.
std::vector<sdr::Nayte> testisignaali(std::size_t n) {
    std::vector<sdr::Nayte> z(n);
    const double beta = 0.5 * kPoikkeama / 1e3;
    for (std::size_t k = 0; k < n; ++k) {
        const double t = static_cast<double>(k) / kFs;
        z[k] = std::polar(1.0, 2 * std::numbers::pi * 200e3 * t +
                                   beta * std::sin(2 * std::numbers::pi *
                                                   1e3 * t));
    }
    return z;
}

// @alku itsetesti
int itsetesti() {
    const std::vector<sdr::Nayte> z = testisignaali(91'200);   // 0,1 s
    std::vector<float> kerralla, lohkoittain;
    {
        std::vector<sdr::Nayte> kopio = z;
        Ketju(200e3).kasittele(kopio, kerralla);
    }
    {
        Ketju ketju(200e3);
        std::uint32_t lcg = 12345;     // toistettavat vaihtelevat koot
        for (std::size_t alku = 0; alku < z.size();) {
            lcg = lcg * 1103515245u + 12345u;
            const std::size_t koko =
                std::min<std::size_t>(1 + (lcg >> 16) % 5000,
                                      z.size() - alku);
            std::vector<sdr::Nayte> lohko(z.begin() + alku,
                                          z.begin() + alku + koko);
            ketju.kasittele(lohko, lohkoittain);
            alku += koko;
        }
    }
    std::printf("lahtonaytteita %zu, lohkoittain %s\n", kerralla.size(),
                kerralla == lohkoittain ? "bitilleen sama" : "ERI");
    // Aanen amplitudi pienimman neliosumman sovituksella (alku pois).
    double s = 0, c = 0;
    for (std::size_t k = 200; k < kerralla.size(); ++k) {
        const double w = 2 * std::numbers::pi * 1e3 *
                         static_cast<double>(k + 1) / (kFs / kDesimointi);
        s += kerralla[k] * std::sin(w);
        c += kerralla[k] * std::cos(w);
    }
    const double n = static_cast<double>(kerralla.size() - 200);
    std::printf("aanen amplitudi %.3f (lahetetty 0.500)\n",
                2 * std::hypot(s, c) / n);
    return kerralla == lohkoittain ? 0 : 1;
}
// @loppu itsetesti

// @alku suodin
int suodin(double kanava_hz) {
    Ketju ketju(kanava_hz);
    std::vector<std::uint8_t> tavut(1 << 16);
    std::vector<sdr::Nayte> lohko;
    std::vector<float> mpx;
    std::size_t luettu;
    while ((luettu = std::fread(tavut.data(), 1, tavut.size(), stdin)) > 0) {
        if (luettu % 2 != 0) {
            std::fputs("pariton tavumaara: I ja Q eivat tasmaa\n", stderr);
            return 1;
        }
        lohko.resize(luettu / 2);
        for (std::size_t k = 0; k < lohko.size(); ++k) {
            lohko[k] = {(tavut[2 * k] - 127.5) / 127.5,
                        (tavut[2 * k + 1] - 127.5) / 127.5};
        }
        mpx.clear();
        ketju.kasittele(lohko, mpx);
        if (std::fwrite(mpx.data(), sizeof(float), mpx.size(), stdout) !=
            mpx.size()) {
            std::fputs("kirjoitus epaonnistui\n", stderr);
            return 1;
        }
    }
    return std::ferror(stdin) ? 1 : 0;
}
// @loppu suodin

// @alku mittaa
int mittaa() {
    std::vector<sdr::Nayte> z = testisignaali(1 << 21);   // 2,3 s
    std::vector<float> mpx;
    Ketju ketju(200e3);
    const auto alku = std::chrono::steady_clock::now();
    for (std::size_t k = 0; k < z.size(); k += 16384) {
        ketju.kasittele(std::span(z).subspan(k, 16384), mpx);
    }
    const std::chrono::duration<double> kesto =
        std::chrono::steady_clock::now() - alku;
    const double nopeus = static_cast<double>(z.size()) / kesto.count();
    std::printf("%.1f MS/s eli %.0f x reaaliaika (912 kS/s)\n",
                nopeus / 1e6, nopeus / kFs);
    return 0;
}
// @loppu mittaa

}  // namespace

int main(int argc, char** argv) {
    const std::vector<std::string_view> arg(argv + 1, argv + argc);
    if (arg.empty()) {
        return itsetesti();
    }
    if (arg.size() == 2 && arg[0] == "--suodin") {
        return suodin(std::atof(arg[1].data()));
    }
    if (arg.size() == 1 && arg[0] == "--mittaa") {
        return mittaa();
    }
    std::fputs("kaytto: ohjelma [--suodin TAAJUUS_HZ | --mittaa]\n", stderr);
    return 2;
}
