// Lohkoittain toimivat vastaanotinosat: NCO, desimoiva FIR ja
// FM-ilmaisin. Jokainen osa sailyttaa tilansa lohkojen valilla, joten
// tulos on bitilleen sama lohkon koosta riippumatta.
#pragma once

#include <complex>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace sdr {

using Nayte = std::complex<double>;

// @alku nco
// Numeerisesti ohjattu oskillaattori: 32 bitin vaiheakkumulaattori ja
// 4096 alkion taulukko. Taajuusresoluutio on fs / 2^32.
class Nco {
public:
    Nco(double taajuus, double fs);
    // Kertoo lohkon oskillaattorilla exp(-j vaihe): siirto alaspain.
    void sekoita(std::span<Nayte> lohko);

private:
    static constexpr int kTaulukkoBitit = 12;
    std::vector<Nayte> taulukko_;
    std::uint32_t vaihe_ = 0;
    std::uint32_t askel_;
};
// @loppu nco

// @alku fir
// Desimoiva FIR: lasketaan vain joka D:s lahto. Historia sailyttaa
// edellisen lohkon viimeiset naytteet.
class FirDesimoija {
public:
    FirDesimoija(std::vector<double> kertoimet, std::size_t desimointi);
    void suodata(std::span<const Nayte> sisaan, std::vector<Nayte>& ulos);

private:
    std::vector<double> h_;
    std::size_t d_;
    std::vector<Nayte> historia_;   // pituus len(h) - 1 + lohko
    std::size_t vaihe_ = 0;         // naytteita seuraavaan lahtoon
};
// @loppu fir

// @alku ilmaisin
class FmIlmaisin {
public:
    FmIlmaisin(double fs, double poikkeama);
    void ilmaise(std::span<const Nayte> sisaan, std::vector<float>& ulos);

private:
    double vahvistus_;
    Nayte edellinen_{};
    bool alussa_ = true;
};
// @loppu ilmaisin

// scipy.signal.firwin-yhteensopiva alipaasto (Hamming-ikkuna).
std::vector<double> alipaasto(std::size_t pituus, double raja, double fs);

}  // namespace sdr
