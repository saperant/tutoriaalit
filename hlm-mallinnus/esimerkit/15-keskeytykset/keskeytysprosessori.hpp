// Prosessorimalli, joka ottaa keskeytyksiä: luvun 11 malli laajennettuna
// CSR-rekistereillä sekä käskyillä csrrw, csrrs, csrrc, mret ja wfi.
#pragma once
#include <cstdint>
#include <vector>

#include <systemc>

#include "../14-prototyyppi/prosessori.hpp"
#include "csr.hpp"

// @alku liitanta
// Keskeytyslinjat ovat tavallisia signaaliportteja. Ne vastaavat
// rekisterin mip bittejä MTIP (ajastin) ja MEIP (ulkoinen), ja linja on
// tasoherkkä: keskeytys on vireillä niin kauan kuin linja on 1.
class KeskeytysProsessori : public Prosessori {
public:
    sc_core::sc_in<bool> ajastin_irq{"ajastin_irq"};
    sc_core::sc_in<bool> ulkoinen_irq{"ulkoinen_irq"};

    explicit KeskeytysProsessori(sc_core::sc_module_name nimi)
        : Prosessori(nimi) {}
    // @loppu liitanta

    // Mittauksia varten: jokainen otettu keskeytys ja paluu.
    struct Otto {
        unsigned syy;            // mcausen numero: 7 tai 11
        sc_core::sc_time aika;   // prosessorin aika ottohetkellä
    };
    std::vector<Otto> otot;
    std::vector<sc_core::sc_time> paluut;  // mret-käskyjen hetket
    std::uint64_t synkronointeja = 0;
    sc_core::sc_time nukuttu;    // wfi:ssä odotettu aika
    bool synkronoi_palatessa = true;  // koetta varten, ks. mret

protected:
    // @alku otto
    std::uint32_t mip() const {
        return (ajastin_irq.read() ? csr::MTI : 0u) |
               (ulkoinen_irq.read() ? csr::MEI : 0u);
    }

    // Kutsutaan käskyjen välissä. Keskeytys otetaan, jos se on vireillä
    // (mip), sallittu lähteelle (mie) ja keskeytykset ovat päällä
    // (mstatus.MIE). Ulkoinen keskeytys menee ajastimen edelle.
    void ota_keskeytys() {
        const std::uint32_t vireilla = mip() & mie_;
        if ((mstatus_ & csr::MIE) == 0 || vireilla == 0) return;
        const unsigned syy = (vireilla & csr::MEI) ? 11 : 7;
        mepc_ = pc_;                       // tähän palataan
        mcause_ = csr::KESKEYTYS | syy;
        mstatus_ = (mstatus_ & ~csr::MIE) | csr::MPIE;  // MPIE = vanha MIE
        pc_ = mtvec_;                      // suora tila: yksi käsittelijä
        otot.push_back({syy, qk_.get_current_time()});
    }
    // @loppu otto

    // @alku synkronointi
    void synkronoi() {
        qk_.sync();
        ++synkronointeja;
    }

    // wfi: prosessori pysähtyy, kunnes jokin sallittu keskeytys on
    // vireillä. Malli tuo ensin simulaatioajan omalle tasalleen ja jää
    // sitten odottamaan linjan nousua: aikaa kuluu, käskyjä ei.
    void nuku() {
        synkronoi();
        const sc_core::sc_time alku = sc_core::sc_time_stamp();
        while ((mip() & mie_) == 0) {
            wait(ajastin_irq.posedge_event() | ulkoinen_irq.posedge_event());
        }
        nukuttu += sc_core::sc_time_stamp() - alku;
        qk_.reset();
    }
    // @loppu synkronointi

    std::uint32_t* rekisteri(std::uint32_t numero) {
        switch (numero) {
        case csr::mstatus: return &mstatus_;
        case csr::mie: return &mie_;
        case csr::mtvec: return &mtvec_;
        case csr::mepc: return &mepc_;
        case csr::mcause: return &mcause_;
        default: return nullptr;
        }
    }

    // @alku jarjestelma
    // rekisteri() palauttaa osoittimen CSR:ään tai nullptr:n.
    bool jarjestelma(std::uint32_t k) override {
        const std::uint32_t rd = k >> 7 & 0x1F, f3 = k >> 12 & 7,
                            rs1 = k >> 15 & 0x1F, numero = k >> 20;
        if (k == 0x73) return Prosessori::jarjestelma(k);  // ecall
        if (k == 0x30200073) {                             // mret
            // Käsittelijä on kuitannut laitteen, mutta linja laskee vasta,
            // kun simulaatioaika saavuttaa kuittaushetken. Ilman
            // synkronointia linja näyttäisi yhä ykköstä.
            if (synkronoi_palatessa) synkronoi();
            const bool mpie = mstatus_ & csr::MPIE;
            mstatus_ = (mstatus_ & ~csr::MIE) | csr::MPIE |
                       (mpie ? csr::MIE : 0u);
            pc_ = mepc_;
            paluut.push_back(qk_.get_current_time());
            return true;
        }
        if (k == 0x10500073) {                             // wfi
            nuku();
            pc_ += 4;
            return true;
        }
        if (f3 < 1 || f3 > 3) return tuntematon(k);
        std::uint32_t* r = rekisteri(numero);
        if (r == nullptr && numero != csr::mip) return tuntematon(k);
        const std::uint32_t vanha = r ? *r : mip();
        const std::uint32_t a = x_[rs1];
        if (r != nullptr) {
            if (f3 == 1) *r = a;                           // csrrw
            else if (rs1 != 0) *r = f3 == 2 ? vanha | a    // csrrs
                                           : vanha & ~a;  // csrrc
        }
        if (rd != 0) x_[rd] = vanha;
        pc_ += 4;
        return true;
    }
    // @loppu jarjestelma

    // @alku aja
    void aja() override {
        const sc_core::sc_time jakso(10, sc_core::SC_NS);
        qk_.reset();
        bool kaynnissa = true;
        while (kaynnissa) {
            ota_keskeytys();                  // käskyrajalla
            const std::uint32_t kasky = lue(pc_, 4);
            kaynnissa = suorita(kasky);
            ++kaskyja;
            qk_.inc(jakso);
            if (qk_.need_sync()) synkronoi();
        }
        qk_.sync();
        sc_core::sc_stop();  // ajastin tuottaisi tapahtumia loputtomiin
    }
    // @loppu aja

private:
    std::uint32_t mstatus_ = 0, mie_ = 0, mtvec_ = 0, mepc_ = 0, mcause_ = 0;
};
