// Ohjelman lataaja virtuaaliprototyypille.
#pragma once
#include <utility>
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>

// @alku lataaja
// Lataa ohjelman muistiin debug-kirjoituksilla, kuten debuggeri tai
// käynnistyslataajan malli tekisi: ei simulaatioaikaa, ei tilastoja.
// start_of_simulation() ajetaan elaboroinnin jälkeen mutta ennen kuin
// yksikään prosessi (myöskään prosessori) käynnistyy.
class Lataaja : public sc_core::sc_module {
public:
    tlm_utils::simple_initiator_socket<Lataaja> socket{"socket"};

    Lataaja(sc_core::sc_module_name nimi, std::vector<unsigned char> kuva)
        : sc_core::sc_module(nimi), kuva_(std::move(kuva)) {}

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
