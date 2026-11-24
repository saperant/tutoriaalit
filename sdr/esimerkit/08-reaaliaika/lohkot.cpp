#include "lohkot.hpp"

#include <cmath>
#include <numbers>
#include <utility>

namespace sdr {

// @alku nco_toteutus
Nco::Nco(double taajuus, double fs)
    : taulukko_(std::size_t{1} << kTaulukkoBitit),
      askel_(static_cast<std::uint32_t>(
          std::llround(taajuus / fs * 4294967296.0) & 0xFFFFFFFF)) {
    for (std::size_t i = 0; i < taulukko_.size(); ++i) {
        const double kulma =
            2 * std::numbers::pi * static_cast<double>(i) /
            static_cast<double>(taulukko_.size());
        taulukko_[i] = std::polar(1.0, -kulma);
    }
}

void Nco::sekoita(std::span<Nayte> lohko) {
    for (Nayte& x : lohko) {
        x *= taulukko_[vaihe_ >> (32 - kTaulukkoBitit)];
        vaihe_ += askel_;   // ylivuoto on tarkoituksellinen: vaihe mod 2pi
    }
}
// @loppu nco_toteutus

// @alku fir_toteutus
FirDesimoija::FirDesimoija(std::vector<double> kertoimet,
                           std::size_t desimointi)
    : h_(std::move(kertoimet)), d_(desimointi),
      historia_(h_.size() - 1) {}

void FirDesimoija::suodata(std::span<const Nayte> sisaan,
                           std::vector<Nayte>& ulos) {
    const std::size_t m = h_.size() - 1;
    historia_.insert(historia_.end(), sisaan.begin(), sisaan.end());
    std::size_t k = vaihe_;
    for (; k < sisaan.size(); k += d_) {
        // Lahto y[n] = sum h[j] x[n - j]; x[n] on historian kohdassa m + k.
        Nayte summa{};
        for (std::size_t j = 0; j <= m; ++j) {
            summa += h_[j] * historia_[m + k - j];
        }
        ulos.push_back(summa);
    }
    vaihe_ = k - sisaan.size();
    historia_.erase(historia_.begin(),
                    historia_.end() - static_cast<std::ptrdiff_t>(m));
}
// @loppu fir_toteutus

// @alku ilmaisin_toteutus
FmIlmaisin::FmIlmaisin(double fs, double poikkeama)
    : vahvistus_(fs / (2 * std::numbers::pi * poikkeama)) {}

void FmIlmaisin::ilmaise(std::span<const Nayte> sisaan,
                         std::vector<float>& ulos) {
    for (const Nayte& z : sisaan) {
        if (!alussa_) {
            ulos.push_back(static_cast<float>(
                std::arg(z * std::conj(edellinen_)) * vahvistus_));
        }
        alussa_ = false;
        edellinen_ = z;
    }
}
// @loppu ilmaisin_toteutus

std::vector<double> alipaasto(std::size_t pituus, double raja, double fs) {
    std::vector<double> h(pituus);
    const double fc = raja / (fs / 2);       // Nyquist-normitettu
    const double keski = static_cast<double>(pituus - 1) / 2;
    double summa = 0;
    for (std::size_t n = 0; n < pituus; ++n) {
        const double t = static_cast<double>(n) - keski;
        const double x = std::numbers::pi * fc * t;
        const double sinc = t == 0 ? 1.0 : std::sin(x) / x;
        const double ikkuna =
            0.54 - 0.46 * std::cos(2 * std::numbers::pi *
                                   static_cast<double>(n) /
                                   static_cast<double>(pituus - 1));
        h[n] = fc * sinc * ikkuna;
        summa += h[n];
    }
    for (double& c : h) {
        c /= summa;                          // tasavahvistus 1
    }
    return h;
}

}  // namespace sdr
