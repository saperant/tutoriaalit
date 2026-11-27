// RV32I-osajoukon käskytason simulaattori (ISS) TLM-aloittajana.
#pragma once
#include <cstdint>
#include <cstring>
#include <iostream>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/tlm_quantumkeeper.h>

// @alku liitanta
// Prosessori näkee muistin ja laitteet vain väylän kautta. RAM-alueelle
// se pyytää DMI-osoittimen; laitteiden rekisterit luetaan b_transportilla.
// Ajallisesti se on LT-malli: jokainen käsky vie yhden 10 ns:n jakson
// ja muistiviiveet lisätään paikalliseen aikaan.
SC_MODULE(Prosessori) {
    tlm_utils::simple_initiator_socket<Prosessori> socket{"socket"};

    std::uint64_t kaskyja = 0, transaktioita = 0, dmi_kayttoja = 0;
    std::uint32_t paluuarvo = 0;

    SC_CTOR(Prosessori) {
        socket.register_invalidate_direct_mem_ptr(this,
                                                  &Prosessori::mitatoi);
        SC_THREAD(aja);
    }
    // @loppu liitanta

    // Tila ja apufunktiot ovat aliluokan käytettävissä: esimerkin
    // 15-keskeytykset prosessori laajentaa tätä mallia.
protected:
    // @alku muistiliikenne
    // Lukee tai kirjoittaa 1-4 tavua. DMI:tä käytetään, jos osoite on
    // voimassa olevan alueen sisällä; muuten tehdään transaktio, ja jos
    // kohde vihjaa DMI:n olevan mahdollinen, osoitinta pyydetään.
    void siirra(tlm::tlm_command komento, std::uint32_t osoite,
                void* data, unsigned pituus) {
        if (dmi_ok_ && osoite >= dmi_.get_start_address() &&
            osoite + pituus - 1 <= dmi_.get_end_address()) {
            unsigned char* p =
                dmi_.get_dmi_ptr() + (osoite - dmi_.get_start_address());
            if (komento == tlm::TLM_READ_COMMAND) {
                std::memcpy(data, p, pituus);
                qk_.inc(dmi_.get_read_latency());
            } else {
                std::memcpy(p, data, pituus);
                qk_.inc(dmi_.get_write_latency());
            }
            ++dmi_kayttoja;
            return;
        }
        tlm::tlm_generic_payload gp;
        gp.set_command(komento);
        gp.set_address(osoite);
        gp.set_data_ptr(static_cast<unsigned char*>(data));
        gp.set_data_length(pituus);
        gp.set_streaming_width(pituus);
        gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
        sc_core::sc_time viive = qk_.get_local_time();
        socket->b_transport(gp, viive);
        qk_.set(viive);
        ++transaktioita;
        if (gp.is_response_error()) {
            std::cerr << "väylävirhe osoitteessa 0x" << std::hex << osoite
                      << " (pc 0x" << pc_ << std::dec << ")\n";
            SC_REPORT_FATAL(name(), gp.get_response_string().c_str());
        }
        if (gp.is_dmi_allowed() && !dmi_ok_) {
            dmi_ok_ = socket->get_direct_mem_ptr(gp, dmi_);
        }
    }

    void mitatoi(sc_dt::uint64, sc_dt::uint64) { dmi_ok_ = false; }
    // @loppu muistiliikenne

    std::uint32_t lue(std::uint32_t osoite, unsigned pituus) {
        std::uint32_t arvo = 0;
        siirra(tlm::TLM_READ_COMMAND, osoite, &arvo, pituus);
        return arvo;
    }

    // @alku dekoodaus
    static std::int32_t imm_i(std::uint32_t k) {
        return static_cast<std::int32_t>(k) >> 20;
    }
    static std::int32_t imm_s(std::uint32_t k) {
        return (static_cast<std::int32_t>(k) >> 25 << 5) |
               static_cast<std::int32_t>(k >> 7 & 0x1F);
    }
    static std::int32_t imm_b(std::uint32_t k) {
        return (static_cast<std::int32_t>(k) >> 31 << 12) |
               static_cast<std::int32_t>((k >> 7 & 1) << 11 |
                                         (k >> 25 & 0x3F) << 5 |
                                         (k >> 8 & 0xF) << 1);
    }
    static std::int32_t imm_j(std::uint32_t k) {
        return (static_cast<std::int32_t>(k) >> 31 << 20) |
               static_cast<std::int32_t>((k >> 12 & 0xFF) << 12 |
                                         (k >> 20 & 1) << 11 |
                                         (k >> 21 & 0x3FF) << 1);
    }
    // @loppu dekoodaus

    // @alku suoritus
    // Suorittaa yhden käskyn. Palauttaa false, kun ohjelma päättyy
    // (ecall). Tuntematon käsky on mallin kannalta kohtalokas virhe.
    bool suorita(std::uint32_t k) {
        const std::uint32_t op = k & 0x7F, rd = k >> 7 & 0x1F,
                            f3 = k >> 12 & 7, rs1 = k >> 15 & 0x1F,
                            rs2 = k >> 20 & 0x1F;
        const std::uint32_t a = x_[rs1], b = x_[rs2];
        std::uint32_t seuraava = pc_ + 4, tulos = 0;
        bool kirjoita = true;
        switch (op) {
        case 0x37: tulos = k & 0xFFFFF000; break;                 // lui
        case 0x13:                                               // OP-IMM
            if (f3 == 0) tulos = a + imm_i(k);                   // addi
            else if (f3 == 7) tulos = a & imm_i(k);              // andi
            else return tuntematon(k);
            break;
        case 0x33:                                               // OP
            if (f3 == 0 && k >> 25 == 0) tulos = a + b;          // add
            else if (f3 == 5 && k >> 25 == 0) tulos = a >> (b & 31);  // srl
            else return tuntematon(k);
            break;
        case 0x03:                                               // LOAD
            if (f3 == 2) tulos = lue(a + imm_i(k), 4);           // lw
            else if (f3 == 4) tulos = lue(a + imm_i(k), 1);      // lbu
            else return tuntematon(k);
            break;
        case 0x23: {                                             // STORE
            if (f3 != 2) return tuntematon(k);                   // sw
            std::uint32_t arvo = b;
            siirra(tlm::TLM_WRITE_COMMAND, a + imm_s(k), &arvo, 4);
            kirjoita = false;
            break;
        }
        case 0x63: {                                             // BRANCH
            const auto sa = static_cast<std::int32_t>(a);
            const auto sb = static_cast<std::int32_t>(b);
            bool hyppaa = false;
            if (f3 == 0) hyppaa = a == b;                        // beq
            else if (f3 == 1) hyppaa = a != b;                   // bne
            else if (f3 == 5) hyppaa = sa >= sb;                 // bge
            else return tuntematon(k);
            if (hyppaa) seuraava = pc_ + imm_b(k);
            kirjoita = false;
            break;
        }
        case 0x6F:                                               // jal
            tulos = pc_ + 4;
            seuraava = pc_ + imm_j(k);
            break;
        case 0x67:                                               // jalr
            tulos = pc_ + 4;
            seuraava = (a + imm_i(k)) & ~1u;
            break;
        case 0x73:                                               // SYSTEM
            return jarjestelma(k);
        default:
            return tuntematon(k);
        }
        if (kirjoita && rd != 0) x_[rd] = tulos;  // x0 on aina nolla
        pc_ = seuraava;
        return true;
    }

    // SYSTEM-käskyistä tämä malli tuntee vain ecallin, joka lopettaa
    // ohjelman. Aliluokka voi lisätä muut (CSR-käskyt, mret, wfi).
    virtual bool jarjestelma(std::uint32_t k) {
        if (k != 0x73) return tuntematon(k);
        paluuarvo = x_[10];
        return false;
    }

    bool tuntematon(std::uint32_t k) {
        std::cerr << "tuntematon käsky 0x" << std::hex << k << " (pc 0x"
                  << pc_ << std::dec << ")\n";
        SC_REPORT_FATAL(name(), "tuntematon käsky");
        return false;
    }
    // @loppu suoritus

    // @alku aja
    virtual void aja() {
        const sc_core::sc_time jakso(10, sc_core::SC_NS);  // 100 MHz
        qk_.reset();
        bool kaynnissa = true;
        while (kaynnissa) {
            const std::uint32_t kasky = lue(pc_, 4);  // käskynhaku
            kaynnissa = suorita(kasky);
            ++kaskyja;
            qk_.inc(jakso);
            if (qk_.need_sync()) {
                qk_.sync();
            }
        }
        qk_.sync();
        // Muilla malleilla ei ole omia prosesseja, joten tapahtumat
        // loppuvat ja sc_start() palaa. Kellotetussa järjestelmässä
        // tässä kutsuttaisiin sc_stop().
    }
    // @loppu aja

    tlm_utils::tlm_quantumkeeper qk_;
    tlm::tlm_dmi dmi_;
    bool dmi_ok_ = false;
    std::uint32_t pc_ = 0;
    std::uint32_t x_[32] = {};
};
