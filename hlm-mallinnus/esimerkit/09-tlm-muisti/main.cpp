// Ensimmäinen TLM-malli: aloittaja ja muisti, b_transport.
#include <cstdint>
#include <iomanip>
#include <iostream>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>

#include "../mallit/muisti.hpp"

using namespace sc_core;

// @alku aloittaja
// Aloittaja tekee sarjan sanan kokoisia luku- ja kirjoitustransaktioita.
// Jokaisen jälkeen se odottaa kohteen annotoiman viiveen, joten
// simulaatioaika etenee transaktio kerrallaan.
SC_MODULE(Aloittaja) {
    tlm_utils::simple_initiator_socket<Aloittaja> socket{"socket"};

    SC_CTOR(Aloittaja) { SC_THREAD(aja); }

    // Palauttaa vastauksen tilan; data luetaan tai kirjoitetaan arvoon.
    tlm::tlm_response_status siirra(tlm::tlm_command komento,
                                    sc_dt::uint64 osoite,
                                    std::uint32_t& arvo,
                                    unsigned char* tavut = nullptr) {
        tlm::tlm_generic_payload gp;
        gp.set_command(komento);
        gp.set_address(osoite);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
        gp.set_data_length(4);
        gp.set_streaming_width(4);
        gp.set_byte_enable_ptr(tavut);
        gp.set_byte_enable_length(tavut ? 4 : 0);
        gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

        sc_time viive = SC_ZERO_TIME;
        socket->b_transport(gp, viive);
        std::cout << std::setw(6) << sc_time_stamp() << ' '
                  << (komento == tlm::TLM_READ_COMMAND ? "luku     "
                                                       : "kirjoitus")
                  << " 0x" << std::hex << std::setw(4) << std::setfill('0')
                  << osoite << " = 0x" << std::setw(8) << arvo << std::dec
                  << std::setfill(' ') << " +" << std::setw(5) << viive
                  << ' ' << gp.get_response_string() << '\n';
        wait(viive);  // aika kuluu vasta täällä
        return gp.get_response_status();
    }
    // @loppu aloittaja

    // @alku testi
    void aja() {
        std::uint32_t arvo = 0;
        for (std::uint32_t i = 0; i < 3; ++i) {
            arvo = 0xC0DE0000 | i;
            siirra(tlm::TLM_WRITE_COMMAND, 4 * i, arvo);
        }
        for (std::uint32_t i = 0; i < 3; ++i) {
            arvo = 0;
            siirra(tlm::TLM_READ_COMMAND, 4 * i, arvo);
        }
        // Virheet: osoite muistin ulkopuolella ja tavumaski, jota
        // muisti ei tue.
        arvo = 0;
        if (siirra(tlm::TLM_READ_COMMAND, 0x1000, arvo) !=
            tlm::TLM_OK_RESPONSE) {
            std::cout << "       aloittaja käsitteli osoitevirheen\n";
        }
        unsigned char tavut[4] = {0xFF, 0xFF, 0, 0};
        arvo = 0xFFFF;
        siirra(tlm::TLM_WRITE_COMMAND, 0, arvo, tavut);
    }
    // @loppu testi
};

int sc_main(int, char*[]) {
    // @alku kytkenta
    Aloittaja aloittaja("aloittaja");
    Muisti muisti("muisti", 4096, sc_time(20, SC_NS), sc_time(30, SC_NS));
    aloittaja.socket.bind(muisti.socket);
    sc_start();
    std::cout << "valmis " << sc_time_stamp() << ", transaktioita "
              << muisti.transaktioita() << '\n';
    // @loppu kytkenta
    return 0;
}
