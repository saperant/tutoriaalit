// Tavallisia SystemC-virheitä. Ohjelma ajaa argumenttina annetun
// tapauksen ja tulostaa simulaattorin virheilmoituksen.
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <systemc>

using namespace sc_core;

// @alku kytkematon
// 1. Portti jää kytkemättä: huomataan elaboroinnin lopussa.
SC_MODULE(Kuuntelija) {
    sc_in<bool> tulo{"tulo"};
    SC_CTOR(Kuuntelija) {}
};
// @loppu kytkematon

// @alku odotus
// 2. wait() SC_METHODissa: metodilla ei ole omaa pinoa, joten se ei
//    voi pysähtyä kesken suorituksen.
SC_MODULE(Odottaja) {
    SC_CTOR(Odottaja) { SC_METHOD(toimi); }
    void toimi() { wait(10, SC_NS); }
};
// @loppu odotus

// @alku ajurit
// 3. Kaksi prosessia kirjoittaa samaa signaalia. Laitteistossa tämä
//    olisi kahden ajurin oikosulku; sc_signal sallii vain yhden
//    kirjoittajan, ellei toisin sanota (SC_MANY_WRITERS).
SC_MODULE(Ajurit) {
    sc_signal<int> vayla{"vayla"};
    SC_CTOR(Ajurit) {
        SC_THREAD(eka);
        SC_THREAD(toka);
    }
    void eka() { vayla.write(1); }
    void toka() {
        wait(1, SC_NS);
        vayla.write(2);
    }
};
// @loppu ajurit

int sc_main(int argc, char* argv[]) {
    const int tapaus = argc > 1 ? std::atoi(argv[1]) : 0;
    try {
        if (tapaus == 1) {
            Kuuntelija k("kuuntelija");
            sc_start();
        } else if (tapaus == 2) {
            Odottaja o("odottaja");
            sc_start();
        } else if (tapaus == 3) {
            Ajurit a("ajurit");
            sc_start();
        } else {
            std::cerr << "käyttö: ohjelma 1|2|3\n";
            return 2;
        }
    } catch (const sc_report& virhe) {
        // Ilmoituksen rivitys vaihtelee; rivitetään se uudelleen.
        std::cout << virhe.get_msg_type() << '\n';
        std::istringstream sanat(virhe.get_msg());
        std::size_t sarake = 0;
        for (std::string sana; sanat >> sana;) {
            if (sarake + sana.size() > 64) {
                std::cout << '\n';
                sarake = 0;
            }
            std::cout << (sarake == 0 ? "  " : " ") << sana;
            sarake += sana.size() + 1;
        }
        std::cout << '\n';
        return 0;
    }
    return 1;
}
