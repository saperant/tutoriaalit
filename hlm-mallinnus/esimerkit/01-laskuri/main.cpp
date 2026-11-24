// Laskurin testipenkki: kello, herätteet ja tulosteet.
#include <iostream>
#include <systemc>

#include "laskuri.hpp"

using namespace sc_core;

// @alku testipenkki
// Herätteet: nollaus kahden jakson ajan, sitten laskenta 18 jaksoa
// kahden jakson tauolla.
SC_MODULE(Heratteet) {
    sc_in<bool> clk{"clk"};
    sc_out<bool> nollaus{"nollaus"};
    sc_out<bool> laske{"laske"};

    SC_CTOR(Heratteet) {
        SC_THREAD(aja);
        sensitive << clk.neg();  // vaihdetaan tuloja laskevalla reunalla
    }

    void aja() {
        nollaus.write(true);
        laske.write(false);
        wait(2);  // kaksi laskevaa reunaa
        nollaus.write(false);
        laske.write(true);
        wait(8);
        laske.write(false);
        wait(2);
        laske.write(true);
        wait(10);
        sc_stop();
    }
};

// Tulostaa laskurin arvon aina, kun se muuttuu.
SC_MODULE(Tarkkailija) {
    sc_in<sc_dt::sc_uint<4>> arvo{"arvo"};
    sc_in<bool> ylivuoto{"ylivuoto"};

    SC_CTOR(Tarkkailija) {
        SC_METHOD(tulosta);
        sensitive << arvo << ylivuoto;
        dont_initialize();
    }

    void tulosta() {
        std::cout << sc_time_stamp() << ": arvo=" << arvo.read();
        if (ylivuoto.read()) {
            std::cout << " ylivuoto";
        }
        std::cout << '\n';
    }
};
// @loppu testipenkki

// @alku main
int sc_main(int, char*[]) {
    // Elaborointi: luodaan moduulit ja kanavat ja kytketään portit.
    sc_clock clk("clk", 10, SC_NS);  // jakso 10 ns, nouseva reuna 0 ns
    sc_signal<bool> nollaus("nollaus");
    sc_signal<bool> laske("laske");
    sc_signal<sc_dt::sc_uint<4>> arvo("arvo");
    sc_signal<bool> ylivuoto("ylivuoto");

    Laskuri laskuri("laskuri");
    laskuri.clk(clk);
    laskuri.nollaus(nollaus);
    laskuri.laske(laske);
    laskuri.arvo(arvo);
    laskuri.ylivuoto(ylivuoto);

    Heratteet heratteet("heratteet");
    heratteet.clk(clk);
    heratteet.nollaus(nollaus);
    heratteet.laske(laske);

    Tarkkailija tarkkailija("tarkkailija");
    tarkkailija.arvo(arvo);
    tarkkailija.ylivuoto(ylivuoto);

    // Simulointi: ajetaan, kunnes testipenkki kutsuu sc_stop().
    sc_start();
    std::cout << "pysähtyi: " << sc_time_stamp() << '\n';
    return 0;
}
// @loppu main
