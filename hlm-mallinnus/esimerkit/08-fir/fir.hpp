// Bittitarkka FIR-suodin: algoritmimalli, jonka laitteisto toteuttaa.
#pragma once
// sc_fixed tulee mukaan vain, jos SC_INCLUDE_FX on määritelty ennen
// ensimmäistä <systemc>-otsaketta. Muuten virheilmoitus on sekava.
#ifndef SC_INCLUDE_FX
#error "määrittele SC_INCLUDE_FX ennen <systemc>-otsaketta"
#endif
#include <array>
#include <cstddef>
#include <systemc>

// @alku tyypit
// Näytteet ja kertoimet ovat Q1.15-lukuja. Tulo on tarkka (32 bittiä,
// Q2.30), ja summaimessa on kolme suojabittiä kahdeksan tulon summalle.
// Ulostulo pyöristetään ja kyllästetään takaisin Q1.15:een.
namespace fir {
constexpr std::size_t TAPIT = 8;
using Nayte = sc_dt::sc_fixed<16, 1, sc_dt::SC_RND, sc_dt::SC_SAT>;
using Kerroin = sc_dt::sc_fixed<16, 1>;
using TarkkaTulo = sc_dt::sc_fixed<32, 2>;
using TarkkaSumma = sc_dt::sc_fixed<35, 5>;

// Alipäästö, kertoimien summa 1 ja itseisarvojen summa 1,28.
inline const std::array<double, TAPIT> KERTOIMET = {
    -0.02, -0.05, 0.17, 0.40, 0.40, 0.17, -0.05, -0.02};
// @loppu tyypit

// @alku suodin
// Suora muoto: y[n] = sum c[k] * x[n-k]. Tyyppiparametrit valitsevat
// välitulosten leveydet, joten samalla koodilla voi tutkia
// vaihtoehtoisia toteutuksia.
template <typename Tulo = TarkkaTulo, typename Summa = TarkkaSumma>
class Suodin {
public:
    Suodin() {
        for (std::size_t k = 0; k < TAPIT; ++k) {
            kertoimet_[k] = KERTOIMET[k];  // kvantisoidaan Q1.15:een
        }
    }

    Nayte suodata(Nayte x) {
        for (std::size_t k = TAPIT - 1; k > 0; --k) {
            viive_[k] = viive_[k - 1];
        }
        viive_[0] = x;
        Summa summa = 0;
        for (std::size_t k = 0; k < TAPIT; ++k) {
            const Tulo tulo = kertoimet_[k] * viive_[k];
            summa += tulo;
        }
        return Nayte(summa);  // pyöristys ja kyllästys
    }

    const std::array<Kerroin, TAPIT>& kertoimet() const {
        return kertoimet_;
    }

private:
    // sc_fixed-oliot alustuvat nollaksi.
    std::array<Kerroin, TAPIT> kertoimet_;
    std::array<Nayte, TAPIT> viive_;
};
// @loppu suodin

// @alku viite
// Liukulukuviite samalla rakenteella ja samoilla (kvantisoiduilla)
// kertoimilla: ero johtuu vain välitulosten bittileveyksistä.
class Viite {
public:
    double suodata(double x) {
        for (std::size_t k = TAPIT - 1; k > 0; --k) {
            viive_[k] = viive_[k - 1];
        }
        viive_[0] = x;
        double summa = 0.0;
        for (std::size_t k = 0; k < TAPIT; ++k) {
            summa += Kerroin(KERTOIMET[k]).to_double() * viive_[k];
        }
        return summa;
    }

private:
    std::array<double, TAPIT> viive_{};
};
// @loppu viite
}  // namespace fir
