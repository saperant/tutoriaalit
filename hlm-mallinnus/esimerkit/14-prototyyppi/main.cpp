// Virtuaaliprototyyppi: prosessori, väylä, RAM, UART ja ajastin.
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <utility>
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/tlm_quantumkeeper.h>

#include "../mallit/ajastin.hpp"
#include "../mallit/muisti.hpp"
#include "../mallit/uart.hpp"
#include "../mallit/vayla.hpp"
#include "prosessori.hpp"
#include "rv32.hpp"

using namespace sc_core;
using namespace rv32;

// @alku ohjelma
// Ohjelma tulostaa tervehdyksen, laskee taulukon summan ja lukee
// ajastimen. Aliohjelmat noudattavat RISC-V:n kutsukäytäntöä:
// argumentti a0:ssa, paluuosoite ra:ssa.
std::vector<unsigned char> ohjelma() {
    Kokoaja k;
    k.la(a0, "tervehdys");
    k.jal(ra, "tulosta");
    k.la(t0, "taulukko");     // summa taulukon 16 sanasta
    k.addi(t1, zero, 16);
    k.addi(s0, zero, 0);
    k.nimio("summaa");
    k.lw(t2, 0, t0);
    k.add(s0, s0, t2);
    k.addi(t0, t0, 4);
    k.addi(t1, t1, -1);
    k.bne(t1, zero, "summaa");
    k.la(a0, "summa");
    k.jal(ra, "tulosta");
    k.addi(a0, s0, 0);
    k.jal(ra, "tulosta_hex");
    k.lui(t0, 0x10001);       // ajastin
    k.lw(s1, 0, t0);
    k.la(a0, "aika");
    k.jal(ra, "tulosta");
    k.addi(a0, s1, 0);
    k.jal(ra, "tulosta_hex");
    k.addi(a0, zero, 0);      // paluuarvo 0
    k.ecall();

    // tulosta(a0 = nollaan päättyvä merkkijono)
    k.nimio("tulosta");
    k.lui(t0, 0x10000);       // UART
    k.nimio("seuraava");
    k.lbu(t1, 0, a0);
    k.beq(t1, zero, "palaa");
    k.nimio("odota");         // odotetaan, että lähetin on vapaana
    k.lw(t2, 4, t0);
    k.andi(t2, t2, 1);
    k.beq(t2, zero, "odota");
    k.sw(t1, 0, t0);
    k.addi(a0, a0, 1);
    k.jal(zero, "seuraava");
    k.nimio("palaa");
    k.jalr(zero, 0, ra);

    // tulosta_hex(a0 = luku): kahdeksan heksanumeroa ja rivinvaihto
    k.nimio("tulosta_hex");
    k.lui(t0, 0x10000);
    k.la(t3, "numerot");
    k.addi(t4, zero, 28);     // siirto: 28, 24, ..., 0
    k.nimio("numero");
    k.srl(t1, a0, t4);
    k.andi(t1, t1, 15);
    k.add(t1, t1, t3);
    k.lbu(t1, 0, t1);
    k.sw(t1, 0, t0);          // tämä UART-malli on aina vapaana
    k.addi(t4, t4, -4);
    k.bge(t4, zero, "numero");
    k.addi(t1, zero, '\n');
    k.sw(t1, 0, t0);
    k.jalr(zero, 0, ra);

    k.nimio("tervehdys");
    k.teksti("Hei virtuaaliprototyypistä!\n");
    k.nimio("summa");
    k.teksti("summa 0x");
    k.nimio("aika");
    k.teksti("ajastin 0x");
    k.nimio("numerot");
    k.teksti("0123456789abcdef");
    k.tasaa();
    k.nimio("taulukko");
    for (std::uint32_t i = 0; i < 16; ++i) {
        k.data(i * i);
    }
    return k.valmis();
}
// @loppu ohjelma

// @alku lataaja
// Lataa ohjelman muistiin debug-kirjoituksilla, kuten debuggeri tai
// käynnistyslataajan malli tekisi: ei simulaatioaikaa, ei tilastoja.
// start_of_simulation() ajetaan elaboroinnin jälkeen mutta ennen kuin
// yksikään prosessi (myöskään prosessori) käynnistyy.
class Lataaja : public sc_module {
public:
    tlm_utils::simple_initiator_socket<Lataaja> socket{"socket"};

    Lataaja(sc_module_name nimi, std::vector<unsigned char> kuva)
        : sc_module(nimi), kuva_(std::move(kuva)) {}

private:
    void start_of_simulation() override {
        tlm::tlm_generic_payload gp;
        gp.set_command(tlm::TLM_WRITE_COMMAND);
        gp.set_address(0);
        gp.set_data_ptr(kuva_.data());
        gp.set_data_length(static_cast<unsigned>(kuva_.size()));
        gp.set_streaming_width(static_cast<unsigned>(kuva_.size()));
        if (socket->transport_dbg(gp) != kuva_.size()) {
            SC_REPORT_FATAL(name(), "ohjelma ei mahdu muistiin");
        }
    }

    std::vector<unsigned char> kuva_;
};
// @loppu lataaja

int sc_main(int, char*[]) {
    // @alku jarjestelma
    tlm_utils::tlm_quantumkeeper::set_global_quantum(sc_time(1, SC_US));
    const std::vector<unsigned char> kuva = ohjelma();
    Prosessori cpu("cpu");
    Lataaja lataaja("lataaja", kuva);
    Vayla vayla("vayla", sc_time(5, SC_NS));
    Muisti ram("ram", 64 * 1024, sc_time(20, SC_NS), sc_time(20, SC_NS));
    Uart uart("uart");
    Ajastin ajastin("ajastin");
    cpu.socket.bind(vayla.kohde);
    lataaja.socket.bind(vayla.kohde);
    vayla.liita(ram.socket, 0x0000'0000, 64 * 1024);
    vayla.liita(uart.socket, 0x1000'0000, 0x8);
    vayla.liita(ajastin.socket, 0x1000'1000, 0x4);
    sc_start();
    // @loppu jarjestelma

    // @alku tilastot
    const double aika_us = sc_time_stamp().to_seconds() * 1e6;
    std::cout << "ohjelma " << kuva.size() << " tavua, paluuarvo "
              << cpu.paluuarvo << "\n"
              << "käskyjä " << cpu.kaskyja << ", aika " << sc_time_stamp()
              << ", " << std::fixed << std::setprecision(1)
              << cpu.kaskyja / aika_us << " käskyä/us\n"
              << "DMI-käyttöjä " << cpu.dmi_kayttoja << ", transaktioita "
              << cpu.transaktioita << " (RAM " << ram.transaktioita()
              << ")\n";
    // @loppu tilastot
    return 0;
}
