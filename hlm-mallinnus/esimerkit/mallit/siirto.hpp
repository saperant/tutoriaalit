// Apufunktio 32-bittisille b_transport-siirroille.
#pragma once
#include <cstdint>

#include <systemc>
#include <tlm>

// @alku siirto
// Tekee yhden sanan siirron. Viive on aloittajan paikallinen aika:
// kohde lisää siihen oman viiveensä. Funktio ei odota.
template <typename Socket>
tlm::tlm_response_status siirra(Socket& socket, tlm::tlm_command komento,
                                sc_dt::uint64 osoite, std::uint32_t& arvo,
                                sc_core::sc_time& viive) {
    tlm::tlm_generic_payload gp;
    gp.set_command(komento);
    gp.set_address(osoite);
    gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
    gp.set_data_length(4);
    gp.set_streaming_width(4);
    gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
    socket->b_transport(gp, viive);
    if (gp.is_response_error()) {
        SC_REPORT_ERROR("siirra", gp.get_response_string().c_str());
    }
    return gp.get_response_status();
}
// @loppu siirto
