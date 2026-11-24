// Synkroninen nelibittinen laskuri: ensimmäinen SystemC-moduuli.
#pragma once
#include <systemc>

// @alku moduuli
// Laskee kellon nousevalla reunalla, kun laske = 1. Nollaus on
// synkroninen ja voittaa laskemisen. ylivuoto on 1 sen jakson ajan,
// jolloin arvo on kääntynyt 15:stä nollaan.
SC_MODULE(Laskuri) {
    sc_core::sc_in<bool> clk{"clk"};
    sc_core::sc_in<bool> nollaus{"nollaus"};
    sc_core::sc_in<bool> laske{"laske"};
    sc_core::sc_out<sc_dt::sc_uint<4>> arvo{"arvo"};
    sc_core::sc_out<bool> ylivuoto{"ylivuoto"};

    SC_CTOR(Laskuri) {
        SC_METHOD(paivita);
        sensitive << clk.pos();
        dont_initialize();
    }

private:
    sc_dt::sc_uint<4> tila = 0;  // rekisteri: säilyy kutsujen välillä

    void paivita() {
        bool kaantyi = false;
        if (nollaus.read()) {
            tila = 0;
        } else if (laske.read()) {
            kaantyi = (tila == 15);
            tila = tila + 1;  // sc_uint<4> kiertää 15 -> 0
        }
        arvo.write(tila);
        ylivuoto.write(kaantyi);
    }
};
// @loppu moduuli
