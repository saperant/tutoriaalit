// Likimäärin ajoitettu (AT) malli: neljä vaihetta ja liukuhihna.
#include <cstdint>
#include <cstring>
#include <deque>
#include <iomanip>
#include <iostream>

#include <systemc>
#include <tlm>
#include <tlm_utils/peq_with_cb_and_phase.h>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/simple_target_socket.h>

#include "muistinhallinta.hpp"

using namespace sc_core;

// Tulostaa vaiheen sillä hetkellä, kun vastaanottaja käsittelee sen.
static void loki(const char* kuka, const tlm::tlm_phase& vaihe,
                 const tlm::tlm_generic_payload& gp) {
    std::cout << std::setw(6) << sc_time_stamp() << "  " << std::left
              << std::setw(11) << vaihe << std::setw(10) << kuka
              << std::right << " #" << gp.get_address() / 4 << '\n';
}

// @alku kohde
// Kohde ottaa vastaan pyynnön 10 ns:ssa (END_REQ) ja vastaa 40 ns
// myöhemmin (BEGIN_RESP). Pyynnöt voivat olla käsittelyssä yhtä aikaa,
// mutta vastauksia on liikkeellä vain yksi kerrallaan: seuraava
// BEGIN_RESP lähtee vasta, kun aloittaja on kuitannut edellisen
// (END_RESP).
SC_MODULE(AtMuisti) {
    tlm_utils::simple_target_socket<AtMuisti> socket{"socket"};
    bool nayta = true;

    SC_CTOR(AtMuisti) : peq_(this, &AtMuisti::vaihe) {
        socket.register_nb_transport_fw(this, &AtMuisti::nb_transport_fw);
    }

    tlm::tlm_sync_enum nb_transport_fw(tlm::tlm_generic_payload& gp,
                                       tlm::tlm_phase& vaihe,
                                       sc_time& viive) {
        if (vaihe == tlm::BEGIN_REQ) {
            gp.acquire();  // pidetään, kunnes vastaus on kuitattu
        }
        peq_.notify(gp, vaihe, viive);  // käsitellään oikealla hetkellä
        return tlm::TLM_ACCEPTED;
    }

private:
    static constexpr tlm::tlm_phase_enum VALMIS = tlm::UNINITIALIZED_PHASE;

    // PEQ (payload event queue) kutsuu tätä, kun vaiheen aika koittaa.
    void vaihe(tlm::tlm_generic_payload& gp, const tlm::tlm_phase& vaihe) {
        if (nayta && vaihe != VALMIS) {
            loki("kohde", vaihe, gp);
        }
        if (vaihe == tlm::BEGIN_REQ) {
            sc_time viive(10, SC_NS);
            tlm::tlm_phase seuraava = tlm::END_REQ;
            socket->nb_transport_bw(gp, seuraava, viive);
            kasittele(gp);
            peq_.notify(gp, VALMIS, sc_time(50, SC_NS));
        } else if (vaihe == VALMIS) {
            valmiit_.push_back(&gp);
            if (valmiit_.size() == 1) {
                vastaa();
            }
        } else if (vaihe == tlm::END_RESP) {
            valmiit_.pop_front();
            gp.release();
            if (!valmiit_.empty()) {
                vastaa();
            }
        }
    }

    void vastaa() {
        tlm::tlm_generic_payload& gp = *valmiit_.front();
        tlm::tlm_phase vaihe = tlm::BEGIN_RESP;
        sc_time viive = SC_ZERO_TIME;
        if (socket->nb_transport_bw(gp, vaihe, viive) ==
            tlm::TLM_COMPLETED) {
            this->vaihe(gp, tlm::END_RESP);  // kuittaus paluuarvona
        }
    }

    void kasittele(tlm::tlm_generic_payload& gp) {
        const sc_dt::uint64 a = gp.get_address();
        if (a + gp.get_data_length() > sizeof data_) {
            gp.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
            return;
        }
        if (gp.is_write()) {
            std::memcpy(data_ + a, gp.get_data_ptr(), gp.get_data_length());
        } else {
            std::memcpy(gp.get_data_ptr(), data_ + a, gp.get_data_length());
        }
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
    }

    tlm_utils::peq_with_cb_and_phase<AtMuisti> peq_;
    std::deque<tlm::tlm_generic_payload*> valmiit_;
    unsigned char data_[256] = {};
};
// @loppu kohde

// @alku at
// AT-aloittaja lähettää seuraavan pyynnön heti, kun edellinen on
// hyväksytty (END_REQ), eikä odota vastausta: pyynnöt menevät
// liukuhihnaan.
SC_MODULE(AtAloittaja) {
    tlm_utils::simple_initiator_socket<AtAloittaja> socket{"socket"};
    sc_time valmis;

    SC_CTOR(AtAloittaja) : peq_(this, &AtAloittaja::vaihe) {
        socket.register_nb_transport_bw(this, &AtAloittaja::nb_transport_bw);
        SC_THREAD(aja);
    }

    void aja() {
        for (std::uint32_t i = 0; i < 4; ++i) {
            tlm::tlm_generic_payload* gp = mm_.varaa();
            gp->acquire();
            data_[i] = 100 + i;
            gp->set_command(tlm::TLM_WRITE_COMMAND);
            gp->set_address(4 * i);
            gp->set_data_ptr(reinterpret_cast<unsigned char*>(&data_[i]));
            gp->set_data_length(4);
            gp->set_streaming_width(4);
            tlm::tlm_phase vaihe = tlm::BEGIN_REQ;
            sc_time viive = SC_ZERO_TIME;
            socket->nb_transport_fw(*gp, vaihe, viive);
            wait(pyynto_hyvaksytty_);  // pyyntöjen poissulkemissääntö
        }
    }

    tlm::tlm_sync_enum nb_transport_bw(tlm::tlm_generic_payload& gp,
                                       tlm::tlm_phase& vaihe,
                                       sc_time& viive) {
        peq_.notify(gp, vaihe, viive);
        return tlm::TLM_ACCEPTED;
    }

private:
    void vaihe(tlm::tlm_generic_payload& gp, const tlm::tlm_phase& vaihe) {
        loki("aloittaja", vaihe, gp);
        if (vaihe == tlm::END_REQ) {
            pyynto_hyvaksytty_.notify();
        } else if (vaihe == tlm::BEGIN_RESP) {
            if (gp.is_response_error()) {
                SC_REPORT_ERROR(name(), gp.get_response_string().c_str());
            }
            tlm::tlm_phase kuittaus = tlm::END_RESP;
            sc_time viive = SC_ZERO_TIME;
            socket->nb_transport_fw(gp, kuittaus, viive);
            gp.release();
            valmis = sc_time_stamp();
        }
    }

    Muistinhallinta mm_;
    tlm_utils::peq_with_cb_and_phase<AtAloittaja> peq_;
    sc_event pyynto_hyvaksytty_;
    std::uint32_t data_[4] = {};
};
// @loppu at

// @alku lt
// Sama työ b_transportilla. simple_target_socket muuntaa kutsun
// kohteen nb_transport-vaiheiksi, joten kohdetta ei tarvitse muuttaa.
SC_MODULE(LtAloittaja) {
    tlm_utils::simple_initiator_socket<LtAloittaja> socket{"socket"};
    sc_time valmis;

    SC_CTOR(LtAloittaja) { SC_THREAD(aja); }

    void aja() {
        for (std::uint32_t i = 0; i < 4; ++i) {
            std::uint32_t arvo = 100 + i;
            tlm::tlm_generic_payload gp;
            gp.set_command(tlm::TLM_WRITE_COMMAND);
            gp.set_address(4 * i);
            gp.set_data_ptr(reinterpret_cast<unsigned char*>(&arvo));
            gp.set_data_length(4);
            gp.set_streaming_width(4);
            sc_time viive = SC_ZERO_TIME;
            socket->b_transport(gp, viive);
            wait(viive);
        }
        valmis = sc_time_stamp();
    }
};
// @loppu lt

int sc_main(int, char*[]) {
    // @alku main
    AtAloittaja at("at");
    AtMuisti at_muisti("at_muisti");
    at.socket.bind(at_muisti.socket);
    LtAloittaja lt("lt");
    AtMuisti lt_muisti("lt_muisti");
    lt_muisti.nayta = false;
    lt.socket.bind(lt_muisti.socket);
    sc_start();
    std::cout << "AT valmis " << at.valmis << ", LT valmis " << lt.valmis
              << '\n';
    // @loppu main
    return 0;
}
