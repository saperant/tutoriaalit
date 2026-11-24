// Ajallinen irrottaminen: kvantin vaikutus nopeuteen ja tarkkuuteen.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/tlm_quantumkeeper.h>

#include "../mallit/ajastin.hpp"
#include "../mallit/muisti.hpp"
#include "../mallit/siirto.hpp"
#include "../mallit/vayla.hpp"

using namespace sc_core;

constexpr sc_dt::uint64 LIPPU = 0x100;                      // RAM:ssa
constexpr sc_dt::uint64 AJASTIN = 0x1000, NAIIVI = 0x2000;  // laitteet
constexpr std::uint32_t VIESTEJA = 20;
const sc_time VALI(200, SC_NS);  // tuottajan laskenta viestien välillä

// Mittausta varten: viestin i lähetyshetki tuottajan omassa ajassa.
// Tavallinen C++-taulukko on mallin ulkopuolinen havaintokanava.
static sc_time lahetetty[VIESTEJA + 1];

// @alku tuottaja
// Tuottaja kirjoittaa viestin numeron muistiin 200 ns:n välein omassa
// paikallisessa ajassaan. Se synkronoi simulaatioajan kanssa vasta, kun
// kvantti on täynnä: muuten se jatkaa ilman kontekstinvaihtoa.
SC_MODULE(Tuottaja) {
    tlm_utils::simple_initiator_socket<Tuottaja> socket{"socket"};
    tlm_utils::tlm_quantumkeeper qk;
    unsigned odotuksia = 0;

    SC_CTOR(Tuottaja) { SC_THREAD(aja); }

    void aja() {
        qk.reset();
        for (std::uint32_t i = 1; i <= VIESTEJA; ++i) {
            qk.inc(VALI);  // laskentaa ennen seuraavaa viestiä
            if (qk.need_sync()) {
                qk.sync();  // wait(paikallinen aika), paikallinen = 0
                ++odotuksia;
            }
            lahetetty[i] = qk.get_current_time();
            sc_time viive = qk.get_local_time();
            siirra(socket, tlm::TLM_WRITE_COMMAND, LIPPU, i, viive);
            qk.set(viive);
        }
        qk.sync();  // lopuksi kulunut aika simulaatioaikaan
    }
};
// @loppu tuottaja

// @alku kuluttaja
// Kuluttaja kyselee lippua 50 ns:n välein ja mittaa, kuinka paljon
// myöhemmin (omassa ajassaan) se näkee kunkin viestin. Samalla se lukee
// kahta ajastinta ja vertaa niiden lukemia omaan aikaansa.
SC_MODULE(Kuluttaja) {
    tlm_utils::simple_initiator_socket<Kuluttaja> socket{"socket"};
    tlm_utils::tlm_quantumkeeper qk;
    unsigned odotuksia = 0;
    unsigned nahtyja = 0, ennen_lahetysta = 0;
    sc_time pienin = sc_max_time(), suurin = SC_ZERO_TIME;
    std::uint32_t ajastinvirhe = 0;

    SC_CTOR(Kuluttaja) { SC_THREAD(aja); }

    void aja() {
        qk.reset();
        std::uint32_t nahty = 0;
        while (nahty < VIESTEJA) {
            qk.inc(sc_time(50, SC_NS));
            if (qk.need_sync()) {
                qk.sync();
                ++odotuksia;
            }
            const sc_time nyt = qk.get_current_time();  // oma aika
            std::uint32_t arvo = 0, oikea = 0, naiivi = 0;
            sc_time viive = qk.get_local_time();
            siirra(socket, tlm::TLM_READ_COMMAND, LIPPU, arvo, viive);
            siirra(socket, tlm::TLM_READ_COMMAND, AJASTIN, oikea, viive);
            siirra(socket, tlm::TLM_READ_COMMAND, NAIIVI, naiivi, viive);
            qk.set(viive);
            ajastinvirhe = std::max(ajastinvirhe, oikea - naiivi);
            if (arvo != nahty) {
                nahty = arvo;
                ++nahtyja;
                const sc_time t = lahetetty[arvo];
                if (nyt < t) {
                    ++ennen_lahetysta;  // syy-yhteys rikkoutui
                } else {
                    pienin = std::min(pienin, nyt - t);
                    suurin = std::max(suurin, nyt - t);
                }
            }
        }
        qk.sync();
    }
};
// @loppu kuluttaja

int sc_main(int argc, char* argv[]) {
    // @alku main
    // Kvantti nanosekunteina komentoriviltä.
    const sc_time kvantti(argc > 1 ? std::atof(argv[1]) : 0.0, SC_NS);
    tlm_utils::tlm_quantumkeeper::set_global_quantum(kvantti);

    Tuottaja tuottaja("tuottaja");
    Kuluttaja kuluttaja("kuluttaja");
    Vayla vayla("vayla", SC_ZERO_TIME);
    Muisti ram("ram", 0x1000, sc_time(10, SC_NS), sc_time(10, SC_NS));
    Ajastin ajastin("ajastin", true);
    Ajastin naiivi("naiivi", false);
    tuottaja.socket.bind(vayla.kohde);
    kuluttaja.socket.bind(vayla.kohde);
    vayla.liita(ram.socket, 0, 0x1000);
    vayla.liita(ajastin.socket, AJASTIN, 4);
    vayla.liita(naiivi.socket, NAIIVI, 4);
    sc_start();

    std::cout << "kvantti " << kvantti << ": odotuksia "
              << tuottaja.odotuksia + kuluttaja.odotuksia << ", loppu "
              << sc_time_stamp() << "\n  nähtiin " << kuluttaja.nahtyja
              << "/" << VIESTEJA << " viestiä";
    if (kuluttaja.pienin <= kuluttaja.suurin) {
        std::cout << ", " << kuluttaja.pienin << " - " << kuluttaja.suurin
                  << " lähetyksen jälkeen";
    }
    if (kuluttaja.ennen_lahetysta > 0) {
        std::cout << ", " << kuluttaja.ennen_lahetysta << " ennen sitä";
    }
    std::cout << "\n  naiivi ajastin jäljessä enintään "
              << kuluttaja.ajastinvirhe << " jaksoa\n";
    // @loppu main
    return 0;
}
