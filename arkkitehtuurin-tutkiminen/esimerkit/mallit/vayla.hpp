// Osoitedekoodaava väylä: monta aloittajaa, monta kohdetta.
#pragma once
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/multi_passthrough_initiator_socket.h>
#include <tlm_utils/multi_passthrough_target_socket.h>

// @alku vayla
// Aloittajat kytketään porttiin kohde, kohteet porttiin ulos funktiolla
// liita(). Väylä valitsee kohteen osoitteen perusteella, muuttaa
// osoitteen kohteen omaksi (alku = 0) ja palauttaa sen ennalleen.
// Väylä ei mallinna kilpailua: aloittajien pyynnöt eivät odota toisiaan.
class Vayla : public sc_core::sc_module {
public:
    tlm_utils::multi_passthrough_target_socket<Vayla> kohde{"kohde"};
    tlm_utils::multi_passthrough_initiator_socket<Vayla> ulos{"ulos"};

    Vayla(sc_core::sc_module_name nimi, sc_core::sc_time viive)
        : sc_core::sc_module(nimi), viive_(viive) {
        kohde.register_b_transport(this, &Vayla::b_transport);
        kohde.register_transport_dbg(this, &Vayla::transport_dbg);
        kohde.register_get_direct_mem_ptr(this, &Vayla::get_direct_mem_ptr);
        ulos.register_invalidate_direct_mem_ptr(this, &Vayla::mitatoi);
    }

    // Kytkee kohteen osoitealueelle [alku, alku + koko).
    void liita(tlm::tlm_target_socket<>& kohteen_socket, sc_dt::uint64 alku,
               sc_dt::uint64 koko) {
        for (const Alue& a : kartta_) {
            if (alku < a.alku + a.koko && a.alku < alku + koko) {
                SC_REPORT_ERROR("Vayla", "päällekkäiset osoitealueet");
            }
        }
        ulos.bind(kohteen_socket);
        kartta_.push_back({alku, koko});
    }
    // @loppu vayla

private:
    struct Alue {
        sc_dt::uint64 alku, koko;
    };

    // @alku dekoodaus
    // Palauttaa kohteen indeksin tai -1, jos osoite ei kuulu kenellekään.
    // Kohteen osoitteeksi asetetaan siirtymä alueen alusta.
    int dekoodaa(tlm::tlm_generic_payload& gp) const {
        const sc_dt::uint64 osoite = gp.get_address();
        for (std::size_t i = 0; i < kartta_.size(); ++i) {
            const Alue& a = kartta_[i];
            if (osoite >= a.alku && osoite - a.alku < a.koko) {
                gp.set_address(osoite - a.alku);
                return static_cast<int>(i);
            }
        }
        gp.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
        return -1;
    }

    void b_transport(int, tlm::tlm_generic_payload& gp,
                     sc_core::sc_time& viive) {
        const sc_dt::uint64 osoite = gp.get_address();
        const int i = dekoodaa(gp);
        if (i >= 0) {
            viive += viive_;  // väylän oma viive
            ulos[i]->b_transport(gp, viive);
            gp.set_address(osoite);
        }
    }
    // @loppu dekoodaus

    unsigned transport_dbg(int, tlm::tlm_generic_payload& gp) {
        const sc_dt::uint64 osoite = gp.get_address();
        const int i = dekoodaa(gp);
        if (i < 0) {
            return 0;
        }
        const unsigned n = ulos[i]->transport_dbg(gp);
        gp.set_address(osoite);
        return n;
    }

    // @alku dmi
    // DMI-alue on kohteen osoitteissa; väylä muuntaa sen takaisin
    // aloittajan osoitteiksi. Mitätöinnit kulkevat samoin takaisinpäin.
    bool get_direct_mem_ptr(int, tlm::tlm_generic_payload& gp,
                            tlm::tlm_dmi& dmi) {
        const sc_dt::uint64 osoite = gp.get_address();
        const int i = dekoodaa(gp);
        if (i < 0) {
            return false;
        }
        const bool ok = ulos[i]->get_direct_mem_ptr(gp, dmi);
        const Alue& a = kartta_[static_cast<std::size_t>(i)];
        dmi.set_start_address(dmi.get_start_address() + a.alku);
        dmi.set_end_address(dmi.get_end_address() + a.alku);
        dmi.set_read_latency(dmi.get_read_latency() + viive_);
        dmi.set_write_latency(dmi.get_write_latency() + viive_);
        gp.set_address(osoite);
        return ok;
    }

    void mitatoi(int i, sc_dt::uint64 alku, sc_dt::uint64 loppu) {
        const Alue& a = kartta_[static_cast<std::size_t>(i)];
        for (unsigned j = 0; j < kohde.size(); ++j) {
            kohde[j]->invalidate_direct_mem_ptr(a.alku + alku,
                                                a.alku + loppu);
        }
    }
    // @loppu dmi

    std::vector<Alue> kartta_;
    sc_core::sc_time viive_;
};
