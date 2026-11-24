// Virtuaaliprototyyppi laitteisto-ohjelmisto-jakoon: sama FIR-suodin
// ohjelmistona prosessorilla ja kiihdyttimellä, jota prosessori ohjaa
// rekistereillä ja joka lukee ja kirjoittaa muistia DMA:lla.
#include <cstdint>
#include <cstdio>
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>

#include "../mallit/muisti.hpp"
#include "../mallit/vayla.hpp"
#include "kiihdytin.hpp"

using namespace sc_core;

constexpr std::uint32_t SISAAN = 0x0000, ULOS = 0x4000, ULOS_HW = 0x8000;
constexpr std::uint32_t REKISTERIT = 0x10000;

// @alku kustannukset
// Ohjelmiston kustannusmalli profiloinnista: kaksi jaksoa tappia kohden
// (lataus ja kertolasku-yhteenlasku välimuistista) ja kymmenen jaksoa
// näytettä kohden silmukan hallintaan. Prosessori 1 GHz.
constexpr int SW_NAYTE_NS = 2 * TAPIT + 10;
// Ajuri: välimuistin huuhtelu 4 ns/rivi (syöte ja tulos) ja keskeytyksen
// käsittely käyttöjärjestelmässä 2 us.
constexpr int HUUHTELU_NS = 4, KESKEYTYS_NS = 2000;
// @loppu kustannukset

SC_MODULE(Prosessori) {
    SC_HAS_PROCESS(Prosessori);
    tlm_utils::simple_initiator_socket<Prosessori> socket{"socket"};
    sc_event* keskeytys = nullptr;

    explicit Prosessori(sc_module_name nimi) : sc_module(nimi) {
        SC_THREAD(aja);
    }

    // Debug-liikenne: alustus ja tarkistus eivät kuluta mallin aikaa.
    void debug(tlm::tlm_command komento, std::uint32_t osoite,
               std::vector<std::int32_t>& data) {
        tlm::tlm_generic_payload gp;
        gp.set_command(komento);
        gp.set_address(osoite);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(data.data()));
        gp.set_data_length(static_cast<unsigned>(4 * data.size()));
        gp.set_streaming_width(static_cast<unsigned>(4 * data.size()));
        socket->transport_dbg(gp);
    }

    void kirjoita(std::uint32_t osoite, std::uint32_t arvo, sc_time& t) {
        tlm::tlm_generic_payload gp;
        gp.set_command(tlm::TLM_WRITE_COMMAND);
        gp.set_address(osoite);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
        gp.set_data_length(4);
        gp.set_streaming_width(4);
        gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
        socket->b_transport(gp, t);
    }

    // @alku ohjelmisto
    sc_time ohjelmisto(int n) {
        const auto koko = static_cast<std::size_t>(n);
        std::vector<std::int32_t> x(koko), y(koko);
        debug(tlm::TLM_READ_COMMAND, SISAAN, x);
        const sc_time alku = sc_time_stamp();
        for (int i = 0; i < n; ++i) y[std::size_t(i)] = fir(x.data(), i);
        wait(sc_time(n * SW_NAYTE_NS, SC_NS));
        debug(tlm::TLM_WRITE_COMMAND, ULOS, y);
        return sc_time_stamp() - alku;
    }
    // @loppu ohjelmisto

    // @alku laitteisto
    sc_time laitteisto(int n) {
        const sc_time alku = sc_time_stamp();
        const int rivit = 2 * 4 * n / 64;  // syöte ja tulos
        sc_time t(rivit * HUUHTELU_NS, SC_NS);
        kirjoita(REKISTERIT + 0, SISAAN, t);
        kirjoita(REKISTERIT + 4, ULOS_HW, t);
        kirjoita(REKISTERIT + 8, static_cast<std::uint32_t>(n), t);
        kirjoita(REKISTERIT + 12, 1, t);
        wait(t);
        wait(*keskeytys);
        wait(sc_time(KESKEYTYS_NS, SC_NS));
        return sc_time_stamp() - alku;
    }
    // @loppu laitteisto

    void aja() {
        std::printf("%6s %10s %10s %8s  %s\n", "n", "ohjelm. us",
                    "kiihd. us", "nopeutus", "tulos");
        for (const int n : {16, 64, 256, 1024, 4096}) {
            const auto koko = static_cast<std::size_t>(n);
            std::vector<std::int32_t> x(koko), a(koko), b(koko);
            for (std::size_t i = 0; i < koko; ++i) {
                x[i] = static_cast<std::int32_t>(i * 37 % 201) - 100;
            }
            debug(tlm::TLM_WRITE_COMMAND, SISAAN, x);
            const double sw = ohjelmisto(n).to_seconds() * 1e6;
            const double hw = laitteisto(n).to_seconds() * 1e6;
            debug(tlm::TLM_READ_COMMAND, ULOS, a);
            debug(tlm::TLM_READ_COMMAND, ULOS_HW, b);
            std::printf("%6d %10.3f %10.3f %8.2f  %s\n", n, sw, hw, sw / hw,
                        a == b ? "samat" : "EROAVAT");
        }
    }
};

int sc_main(int, char*[]) {
    // @alku kokoonpano
    Prosessori cpu("cpu");
    Kiihdytin fir_hw("fir");
    Vayla vayla("vayla", sc_time(2, SC_NS));
    Muisti ram("ram", 0x10000, sc_time(20, SC_NS), sc_time(20, SC_NS));
    cpu.socket.bind(vayla.kohde);
    fir_hw.dma.bind(vayla.kohde);
    vayla.liita(ram.socket, 0, 0x10000);
    vayla.liita(fir_hw.rekisterit, REKISTERIT, 0x100);
    cpu.keskeytys = &fir_hw.valmis;
    // @loppu kokoonpano
    sc_start();
    return 0;
}
