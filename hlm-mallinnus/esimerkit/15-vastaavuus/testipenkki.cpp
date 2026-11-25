// Verilatorin kääntämä RTL ja bittitarkka malli samassa simulaatiossa.
#include <cstdint>
#include <deque>
#include <iostream>
#include <random>

#include <systemc>

#include "../08-fir/fir.hpp"
#include "Vfir.h"

using namespace sc_core;

// Q1.15-luvun ja 16-bittisen kokonaisluvun muunnokset.
static std::int16_t raaka(const fir::Nayte& x) {
    return static_cast<std::int16_t>(x.to_double() * 32768.0);
}
static fir::Nayte nayte(std::int16_t r) { return r / 32768.0; }

// @alku herate
// Syöttää näytteitä laskevalla kellonreunalla. Jokaisen hyväksytyn
// näytteen odotettu tulos lasketaan heti mallilla ja jonotetaan.
SC_MODULE(Herate) {
    sc_in<bool> clk{"clk"};
    sc_out<bool> rst{"rst"}, kelpaa{"kelpaa"};
    sc_out<std::uint32_t> x{"x"};
    std::deque<std::int16_t>* odotetut = nullptr;

    SC_CTOR(Herate) {
        SC_THREAD(aja);
        sensitive << clk.neg();
    }

    void syota(std::int16_t arvo) {
        x.write(static_cast<std::uint16_t>(arvo));
        kelpaa.write(true);
        odotetut->push_back(raaka(malli_.suodata(nayte(arvo))));
        wait();
    }

    void aja() {
        rst.write(true);
        wait(2);
        rst.write(false);
        // Suunnatut tapaukset: impulssi ja pahin tapaus (saturaatio).
        syota(32767);
        for (int i = 0; i < 8; ++i) syota(0);
        for (int i = 0; i < 16; ++i) {
            syota(fir::KERTOIMET[7 - i % 8] < 0 ? -32768 : 32767);
        }
        // Satunnaiset näytteet; joka neljännellä jaksolla tauko.
        std::mt19937 satunnainen(2026);  // kiinteä siemen: toistettava
        for (int i = 0; i < 2000; ++i) {
            if (i % 4 == 3) {
                kelpaa.write(false);
                wait();
            }
            syota(static_cast<std::int16_t>(satunnainen() >> 16));
        }
        kelpaa.write(false);
        wait(3);
        sc_stop();
    }

private:
    fir::Suodin<> malli_;
};
// @loppu herate

// @alku vertailija
// Vertaa RTL:n tulosta mallin odottamaan nousevalla reunalla.
SC_MODULE(Vertailija) {
    sc_in<bool> clk{"clk"};
    sc_in<bool> kelpaa{"kelpaa"};
    sc_in<std::uint32_t> y{"y"};
    std::deque<std::int16_t>* odotetut = nullptr;
    unsigned verrattu = 0, virheita = 0;

    SC_CTOR(Vertailija) {
        SC_METHOD(vertaa);
        sensitive << clk.pos();
        dont_initialize();
    }

    void vertaa() {
        if (!kelpaa.read()) {
            return;
        }
        const auto rtl = static_cast<std::int16_t>(y.read() & 0xFFFF);
        const std::int16_t odotettu = odotetut->front();
        odotetut->pop_front();
        if (rtl != odotettu && ++virheita <= 3) {
            std::cout << "  ero näytteessä " << verrattu << " ("
                      << sc_time_stamp() << "): RTL " << rtl << ", malli "
                      << odotettu << '\n';
        }
        ++verrattu;
    }
};
// @loppu vertailija

int sc_main(int argc, char* argv[]) {
    // @alku main
    Verilated::commandArgs(argc, argv);
    // sc_stop() tulostaa oletuksena ilmoituksen; vaimennetaan se.
    sc_report_handler::set_actions("/OSCI/SystemC", SC_INFO, SC_DO_NOTHING);
    sc_clock clk("clk", 10, SC_NS);
    sc_signal<bool> rst("rst"), sisaan("sisaan"), ulos("ulos");
    sc_signal<std::uint32_t> x("x"), y("y");
    std::deque<std::int16_t> odotetut;

    Vfir dut("dut");  // Verilatorin tuottama SystemC-moduuli
    dut.clk(clk);
    dut.rst(rst);
    dut.sisaan_kelpaa(sisaan);
    dut.x(x);
    dut.ulos_kelpaa(ulos);
    dut.y(y);

    Herate herate("herate");
    herate.clk(clk);
    herate.rst(rst);
    herate.kelpaa(sisaan);
    herate.x(x);
    herate.odotetut = &odotetut;
    Vertailija vertailija("vertailija");
    vertailija.clk(clk);
    vertailija.kelpaa(ulos);
    vertailija.y(y);
    vertailija.odotetut = &odotetut;

    sc_start();
    dut.final();
    std::cout << "  verrattu " << vertailija.verrattu << " näytettä, eroja "
              << vertailija.virheita << ", jonoon jäi " << odotetut.size()
              << '\n';
    return vertailija.virheita == 0 ? 0 : 1;
    // @loppu main
}
