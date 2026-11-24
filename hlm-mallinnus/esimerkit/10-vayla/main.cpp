// Väylä, osoitekartta ja oheislaitteet.
#include <cstdint>
#include <iomanip>
#include <iostream>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>

#include "../mallit/ajastin.hpp"
#include "../mallit/muisti.hpp"
#include "../mallit/uart.hpp"
#include "../mallit/vayla.hpp"

using namespace sc_core;

// @alku kartta
// Järjestelmän osoitekartta.
namespace kartta {
constexpr sc_dt::uint64 RAM = 0x0000'0000, RAM_KOKO = 64 * 1024;
constexpr sc_dt::uint64 UART = 0x1000'0000, UART_KOKO = 0x8;
constexpr sc_dt::uint64 AJASTIN = 0x1000'1000, AJASTIN_KOKO = 0x4;
}  // namespace kartta
// @loppu kartta

SC_MODULE(Ohjelmisto) {
    tlm_utils::simple_initiator_socket<Ohjelmisto> socket{"socket"};

    SC_CTOR(Ohjelmisto) { SC_THREAD(aja); }

    // Yksi 32-bittinen siirto; palauttaa vastauksen tilan.
    tlm::tlm_response_status siirra(tlm::tlm_command komento,
                                    sc_dt::uint64 osoite,
                                    std::uint32_t& arvo) {
        tlm::tlm_generic_payload gp;
        gp.set_command(komento);
        gp.set_address(osoite);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
        gp.set_data_length(4);
        gp.set_streaming_width(4);
        gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
        sc_time viive = SC_ZERO_TIME;
        socket->b_transport(gp, viive);
        wait(viive);
        if (gp.is_response_error()) {
            std::cout << sc_time_stamp() << ": 0x" << std::hex << osoite
                      << std::dec << ": " << gp.get_response_string()
                      << '\n';
        }
        return gp.get_response_status();
    }

    std::uint32_t lue(sc_dt::uint64 osoite) {
        std::uint32_t arvo = 0;
        siirra(tlm::TLM_READ_COMMAND, osoite, arvo);
        return arvo;
    }

    void kirjoita(sc_dt::uint64 osoite, std::uint32_t arvo) {
        siirra(tlm::TLM_WRITE_COMMAND, osoite, arvo);
    }

    // @alku ohjelma
    // Ohjelmiston näkökulma: kaikki laitteet ovat osoitteita.
    void aja() {
        for (const char merkki : std::string("Hei väylältä!\n")) {
            while ((lue(kartta::UART + 0x4) & 1) == 0) {
            }
            kirjoita(kartta::UART, static_cast<unsigned char>(merkki));
        }
        std::cout << sc_time_stamp() << ": ajastin "
                  << lue(kartta::AJASTIN) << " jaksoa\n";
        kirjoita(kartta::RAM + 0x100, 0x1234'5678);
        lue(0x2000'0000);           // kartoittamaton osoite
        kirjoita(kartta::AJASTIN, 0);  // vain luettava rekisteri

        // Debug-luku ei kuluta aikaa eikä näy laitteille.
        std::uint32_t arvo = 0;
        tlm::tlm_generic_payload gp;
        gp.set_command(tlm::TLM_READ_COMMAND);
        gp.set_address(kartta::RAM + 0x100);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
        gp.set_data_length(4);
        gp.set_streaming_width(4);
        const unsigned n = socket->transport_dbg(gp);
        std::cout << sc_time_stamp() << ": debug-luku " << n
                  << " tavua: 0x" << std::hex << arvo << std::dec << '\n';
    }
    // @loppu ohjelma
};

int sc_main(int, char*[]) {
    // @alku kytkenta
    Ohjelmisto ohjelmisto("ohjelmisto");
    Vayla vayla("vayla", sc_time(5, SC_NS));
    Muisti ram("ram", kartta::RAM_KOKO, sc_time(20, SC_NS),
               sc_time(20, SC_NS));
    Uart uart("uart");
    Ajastin ajastin("ajastin");

    ohjelmisto.socket.bind(vayla.kohde);
    vayla.liita(ram.socket, kartta::RAM, kartta::RAM_KOKO);
    vayla.liita(uart.socket, kartta::UART, kartta::UART_KOKO);
    vayla.liita(ajastin.socket, kartta::AJASTIN, kartta::AJASTIN_KOKO);
    // @loppu kytkenta

    sc_start();
    std::cout << "valmis " << sc_time_stamp() << ", RAM-transaktioita "
              << ram.transaktioita() << '\n';
    return 0;
}
