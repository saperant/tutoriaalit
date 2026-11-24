// Yhteinen pohja 32-bittisille rekisterilohkoille (oheislaitteet).
#pragma once
#include <cstdint>
#include <cstring>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_target_socket.h>

// @alku rekisterit
// Oheislaite, jonka rekisterit ovat 32-bittisiä ja tasattuja. Aliluokka
// toteuttaa lue() ja kirjoita(), jotka palauttavat vastauksen tilan,
// esimerkiksi osoitevirheen tuntemattomalle rekisterille. Pohja
// tarkistaa pyynnön muodon ja lisää käsittelyviiveen.
class Rekisterilohko : public sc_core::sc_module {
public:
    tlm_utils::simple_target_socket<Rekisterilohko> socket{"socket"};

protected:
    Rekisterilohko(sc_core::sc_module_name nimi, sc_core::sc_time viive)
        : sc_core::sc_module(nimi), viive_(viive) {
        socket.register_b_transport(this, &Rekisterilohko::b_transport);
    }

    // aika on hetki, jolloin aloittajan kello on pyynnön kohdalla:
    // simulaatioaika + annotoitu viive.
    using Tila = tlm::tlm_response_status;
    virtual Tila lue(sc_dt::uint64 osoite, std::uint32_t& arvo,
                     const sc_core::sc_time& aika) = 0;
    virtual Tila kirjoita(sc_dt::uint64 osoite, std::uint32_t arvo,
                          const sc_core::sc_time& aika) = 0;

private:
    void b_transport(tlm::tlm_generic_payload& gp, sc_core::sc_time& viive) {
        const sc_dt::uint64 osoite = gp.get_address();
        if (gp.get_data_length() != 4 || osoite % 4 != 0 ||
            gp.get_streaming_width() != 4) {
            gp.set_response_status(tlm::TLM_BURST_ERROR_RESPONSE);
            return;
        }
        if (gp.get_byte_enable_ptr() != nullptr) {
            gp.set_response_status(tlm::TLM_BYTE_ENABLE_ERROR_RESPONSE);
            return;
        }
        const sc_core::sc_time aika = sc_core::sc_time_stamp() + viive;
        std::uint32_t arvo = 0;
        Tila tila = tlm::TLM_OK_RESPONSE;
        if (gp.is_read()) {
            tila = lue(osoite, arvo, aika);
            std::memcpy(gp.get_data_ptr(), &arvo, 4);  // pieni tavujärjestys
        } else if (gp.is_write()) {
            std::memcpy(&arvo, gp.get_data_ptr(), 4);
            tila = kirjoita(osoite, arvo, aika);
        }
        if (tila == tlm::TLM_OK_RESPONSE) {
            viive += viive_;
        }
        gp.set_response_status(tila);
    }

    sc_core::sc_time viive_;
};
// @loppu rekisterit
