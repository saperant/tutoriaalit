// Tuottaja ja hitaampi kuluttaja oman jonokanavan kautta.
#include <iostream>
#include <systemc>

#include "jono.hpp"

using namespace sc_core;

// @alku moduulit
// Näytteistin tuottaa näytteen 10 ns:n välein.
SC_MODULE(Naytteistin) {
    sc_port<JonoKirjoitus<int>> ulos{"ulos"};

    SC_CTOR(Naytteistin) { SC_THREAD(aja); }

    void aja() {
        for (int nayte = 1; nayte <= 6; ++nayte) {
            wait(10, SC_NS);
            ulos->kirjoita(nayte);  // pysähtyy, jos jono on täynnä
            std::cout << sc_time_stamp() << ": kirjoitettu " << nayte
                      << '\n';
        }
    }
};

// Suodin käsittelee näytteen 25 ns:ssa.
SC_MODULE(Suodin) {
    sc_port<JonoLuku<int>> sisaan{"sisaan"};

    SC_CTOR(Suodin) { SC_THREAD(aja); }

    void aja() {
        for (;;) {
            const int nayte = sisaan->lue();
            std::cout << sc_time_stamp() << ":   luettu " << nayte
                      << ", jonossa " << sisaan->maara() << '\n';
            wait(25, SC_NS);
        }
    }
};
// @loppu moduulit

int sc_main(int, char*[]) {
    // @alku kytkenta
    Jono<int> jono("jono", 2);
    Naytteistin naytteistin("naytteistin");
    Suodin suodin("suodin");
    naytteistin.ulos(jono);  // portti kytketään kanavaan, joka
    suodin.sisaan(jono);     // toteuttaa portin rajapinnan
    sc_start();
    std::cout << "valmis " << sc_time_stamp() << '\n';
    // @loppu kytkenta
    return 0;
}
