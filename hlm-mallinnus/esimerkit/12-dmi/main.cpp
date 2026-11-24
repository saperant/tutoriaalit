// Suora muistiväylä (DMI), mitätöinti ja debug-liikenne.
#include <cstdint>
#include <cstring>
#include <iostream>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/tlm_quantumkeeper.h>

#include "../mallit/muisti.hpp"
#include "../mallit/vayla.hpp"

using namespace sc_core;

constexpr sc_dt::uint64 RAM = 0x8000'0000, KOKO = 0x1000;

// @alku lukija
// Lukee muistia sana kerrallaan. Jos kohde on vihjannut DMI:n olevan
// mahdollinen, lukija pyytää osoittimen ja lukee sen jälkeen suoraan
// muistista. Viive lisätään itse DMI:n ilmoittamana.
SC_MODULE(Lukija) {
    tlm_utils::simple_initiator_socket<Lukija> socket{"socket"};
    tlm_utils::tlm_quantumkeeper qk;
    bool kayta_dmi = true;
    unsigned transaktioita = 0, dmi_lukuja = 0, dmi_pyyntoja = 0;
    std::uint32_t summa = 0;

    SC_CTOR(Lukija) {
        socket.register_invalidate_direct_mem_ptr(this, &Lukija::mitatoi);
        SC_THREAD(aja);
    }

    std::uint32_t lue(sc_dt::uint64 osoite) {
        std::uint32_t arvo = 0;
        if (dmi_voimassa_ && osoite >= dmi_.get_start_address() &&
            osoite + 3 <= dmi_.get_end_address()) {
            const sc_dt::uint64 siirto = osoite - dmi_.get_start_address();
            std::memcpy(&arvo, dmi_.get_dmi_ptr() + siirto, 4);
            qk.inc(dmi_.get_read_latency());
            ++dmi_lukuja;
            return arvo;
        }
        tlm::tlm_generic_payload gp;
        gp.set_command(tlm::TLM_READ_COMMAND);
        gp.set_address(osoite);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
        gp.set_data_length(4);
        gp.set_streaming_width(4);
        gp.set_dmi_allowed(false);
        sc_time viive = qk.get_local_time();
        socket->b_transport(gp, viive);
        qk.set(viive);
        ++transaktioita;
        if (gp.is_response_error()) {
            SC_REPORT_ERROR(name(), gp.get_response_string().c_str());
        }
        if (kayta_dmi && gp.is_dmi_allowed()) {
            ++dmi_pyyntoja;
            dmi_voimassa_ = socket->get_direct_mem_ptr(gp, dmi_) &&
                            dmi_.is_read_allowed();
        }
        return arvo;
    }

    void mitatoi(sc_dt::uint64 alku, sc_dt::uint64 loppu) {
        if (dmi_voimassa_ && alku <= dmi_.get_end_address() &&
            loppu >= dmi_.get_start_address()) {
            dmi_voimassa_ = false;
            std::cout << sc_time_stamp() << ": " << name()
                      << ": DMI mitätöity\n";
        }
    }
    // @loppu lukija

    // @alku aja
    // Laskee muistin sanojen summan kahdesti.
    void aja() {
        qk.reset();
        for (int kierros = 0; kierros < 2; ++kierros) {
            for (sc_dt::uint64 a = RAM; a < RAM + KOKO; a += 4) {
                summa += lue(a);
                if (qk.need_sync()) {
                    qk.sync();
                }
            }
        }
        qk.sync();
        std::cout << sc_time_stamp() << ": " << name() << " valmis\n";
    }
    // @loppu aja

private:
    tlm::tlm_dmi dmi_;
    bool dmi_voimassa_ = false;
};

// @alku hallinta
// Täyttää muistin debug-kirjoituksilla (ei aikaa) ja mitätöi DMI:n
// kesken ajon, kuten muistikartan muutos tekisi.
SC_MODULE(Hallinta) {
    tlm_utils::simple_initiator_socket<Hallinta> socket{"socket"};
    Muisti* ram = nullptr;

    SC_CTOR(Hallinta) { SC_THREAD(aja); }

    void aja() {
        for (std::uint32_t i = 0; i < KOKO / 4; ++i) {
            std::uint32_t arvo = i;
            tlm::tlm_generic_payload gp;
            gp.set_command(tlm::TLM_WRITE_COMMAND);
            gp.set_address(RAM + 4 * i);
            gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
            gp.set_data_length(4);
            gp.set_streaming_width(4);
            socket->transport_dbg(gp);
        }
        wait(30, SC_US);
        ram->mitatoi_dmi();
    }
};
// @loppu hallinta

int sc_main(int, char*[]) {
    // @alku main
    tlm_utils::tlm_quantumkeeper::set_global_quantum(sc_time(1, SC_US));
    Lukija ilman("ilman_dmi");
    ilman.kayta_dmi = false;
    Lukija dmi("dmi");
    Hallinta hallinta("hallinta");
    Vayla vayla("vayla", sc_time(5, SC_NS));
    Muisti ram("ram", KOKO, sc_time(20, SC_NS), sc_time(20, SC_NS));
    hallinta.ram = &ram;
    ilman.socket.bind(vayla.kohde);
    dmi.socket.bind(vayla.kohde);
    hallinta.socket.bind(vayla.kohde);
    vayla.liita(ram.socket, RAM, KOKO);
    sc_start();
    for (const Lukija* l : {&ilman, &dmi}) {
        std::cout << l->name() << ": summa " << l->summa << ", b_transport "
                  << l->transaktioita << ", DMI-lukuja " << l->dmi_lukuja
                  << ", DMI-pyyntöjä " << l->dmi_pyyntoja << '\n';
    }
    // @loppu main
    return 0;
}
