// TLM-2.0-muistimalli: b_transport, debug-liikenne ja DMI.
#pragma once
#include <cstring>
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_target_socket.h>

// @alku muisti
// Muisti, jonka osoitteet alkavat nollasta. Luku ja kirjoitus lisäävät
// viivettä annotoituun aikaan; malli ei itse odota (wait), joten sitä
// voi kutsua myös SC_METHODista ja ajallisesti irrotetusta koodista.
class Muisti : public sc_core::sc_module {
public:
    tlm_utils::simple_target_socket<Muisti> socket{"socket"};

    Muisti(sc_core::sc_module_name nimi, std::size_t koko,
           sc_core::sc_time luku, sc_core::sc_time kirjoitus)
        : sc_core::sc_module(nimi), data_(koko, 0), luku_(luku),
          kirjoitus_(kirjoitus) {
        socket.register_b_transport(this, &Muisti::b_transport);
        socket.register_transport_dbg(this, &Muisti::transport_dbg);
        socket.register_get_direct_mem_ptr(this,
                                           &Muisti::get_direct_mem_ptr);
    }

    unsigned long transaktioita() const { return transaktioita_; }
    // @loppu muisti

    // @alku mitatoi
    // Esimerkiksi muistikartan muutos: aloittajien DMI-osoittimet
    // eivät enää ole voimassa.
    void mitatoi_dmi() {
        socket->invalidate_direct_mem_ptr(0, data_.size() - 1);
    }
    // @loppu mitatoi

private:
    // @alku tarkistus
    // Tarkistaa, että kohde pystyy palvelemaan pyynnön. Virhe palautetaan
    // vastauksen tilana; aloittaja päättää, mitä virheelle tehdään.
    bool kelpaa(tlm::tlm_generic_payload& gp) const {
        const sc_dt::uint64 osoite = gp.get_address();
        const unsigned pituus = gp.get_data_length();
        if (osoite >= data_.size() || pituus > data_.size() - osoite) {
            gp.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
        } else if (gp.get_byte_enable_ptr() != nullptr) {
            gp.set_response_status(tlm::TLM_BYTE_ENABLE_ERROR_RESPONSE);
        } else if (gp.get_streaming_width() < pituus) {
            gp.set_response_status(tlm::TLM_BURST_ERROR_RESPONSE);
        } else {
            return true;
        }
        return false;
    }

    void kopioi(tlm::tlm_generic_payload& gp) {
        unsigned char* oma = &data_[gp.get_address()];
        if (gp.is_read()) {
            std::memcpy(gp.get_data_ptr(), oma, gp.get_data_length());
        } else if (gp.is_write()) {
            std::memcpy(oma, gp.get_data_ptr(), gp.get_data_length());
        }
    }
    // @loppu tarkistus

    // @alku b_transport
    void b_transport(tlm::tlm_generic_payload& gp, sc_core::sc_time& viive) {
        ++transaktioita_;
        if (!kelpaa(gp)) {
            return;
        }
        kopioi(gp);
        viive += gp.is_read() ? luku_ : kirjoitus_;
        gp.set_dmi_allowed(true);  // vihje: suora pääsy olisi mahdollinen
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
    }
    // @loppu b_transport

    // @alku dbg
    // Debug-liikenne: ei viivettä, ei sivuvaikutuksia, ei tilastoja.
    unsigned transport_dbg(tlm::tlm_generic_payload& gp) {
        if (!kelpaa(gp)) {
            return 0;
        }
        kopioi(gp);
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
        return gp.get_data_length();
    }
    // @loppu dbg

    // @alku dmi
    // DMI: annetaan aloittajalle osoitin koko muistiin ja viiveet, joita
    // sen pitää itse lisätä aikaansa.
    bool get_direct_mem_ptr(tlm::tlm_generic_payload&, tlm::tlm_dmi& dmi) {
        dmi.set_dmi_ptr(data_.data());
        dmi.set_start_address(0);
        dmi.set_end_address(data_.size() - 1);
        dmi.set_read_latency(luku_);
        dmi.set_write_latency(kirjoitus_);
        dmi.allow_read_write();
        return true;
    }
    // @loppu dmi

    std::vector<unsigned char> data_;
    sc_core::sc_time luku_, kirjoitus_;
    unsigned long transaktioita_ = 0;
};
