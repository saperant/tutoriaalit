// Keskeytyksen antavat oheislaitteet: jaksollinen ajastin ja
// vastaanottava sarjaportti. Molemmat laajentavat yhteisiä malleja.
#pragma once
#include <cstdint>
#include <vector>

#include <systemc>

#include "../mallit/ajastin.hpp"
#include "../mallit/uart.hpp"

// @alku tikkiajastin
// Rekisterit: 0x0 LASKURI (kuten Ajastin), 0x4 JAKSO (kellojaksoina;
// kirjoitus käynnistää jaksolliset keskeytykset, nolla pysäyttää),
// 0x8 TILA (ykkösen kirjoitus bittiin 0 kuittaa keskeytyksen).
class Tikkiajastin : public Ajastin {
public:
    sc_core::sc_out<bool> irq{"irq"};        // keskeytyslinja, aktiivinen 1
    std::vector<sc_core::sc_time> nousut;    // linjan nousuhetket
    std::vector<sc_core::sc_time> laskut;    // linjan laskuhetket
    unsigned menetetyt = 0;  // tikki tuli, kun edellinen oli kuittaamatta

    SC_HAS_PROCESS(Tikkiajastin);
    explicit Tikkiajastin(sc_core::sc_module_name nimi) : Ajastin(nimi) {
        SC_METHOD(linja);
        sensitive << tikki_ << kuittaus_;
        dont_initialize();
    }
    // @loppu tikkiajastin

protected:
    Tila lue(sc_dt::uint64 osoite, std::uint32_t& arvo,
             const sc_core::sc_time& aika) override {
        if (osoite == 0x4) {
            arvo = jakso_;
            return tlm::TLM_OK_RESPONSE;
        }
        return Ajastin::lue(osoite, arvo, aika);
    }

    // @alku kirjoitus
    // Kirjoitus tapahtuu aloittajan ajassa (aika), joka voi olla
    // simulaatioaikaa edellä. Linjan muutokset ajoitetaan sen mukaan:
    // tapahtuma laukeaa, kun simulaatioaika saavuttaa oikean hetken.
    Tila kirjoita(sc_dt::uint64 osoite, std::uint32_t arvo,
                  const sc_core::sc_time& aika) override {
        const sc_core::sc_time edella = aika - sc_core::sc_time_stamp();
        if (osoite == 0x4) {
            jakso_ = arvo;
            tikki_.cancel();
            if (jakso_ != 0) tikki_.notify(edella + jakson_aika());
            return tlm::TLM_OK_RESPONSE;
        }
        if (osoite == 0x8) {
            if (arvo & 1) kuittaus_.notify(edella);
            return tlm::TLM_OK_RESPONSE;
        }
        return tlm::TLM_ADDRESS_ERROR_RESPONSE;
    }
    // @loppu kirjoitus

private:
    sc_core::sc_time jakson_aika() const {
        return jakso_ * sc_core::sc_time(10, sc_core::SC_NS);
    }

    // @alku linja
    // Ainoa prosessi, joka ajaa linjaa. Se herää oikealla
    // simulaatiohetkellä, joten linjan reunat ovat tarkkoja kvantista
    // riippumatta.
    void linja() {
        if (kuittaus_.triggered() && odottaa_) {
            odottaa_ = false;
            laskut.push_back(sc_core::sc_time_stamp());
        }
        if (tikki_.triggered()) {
            if (odottaa_) {
                ++menetetyt;
            } else {
                odottaa_ = true;
                nousut.push_back(sc_core::sc_time_stamp());
            }
            tikki_.notify(jakson_aika());  // seuraava tikki
        }
        irq.write(odottaa_);
    }
    // @loppu linja

    sc_core::sc_event tikki_, kuittaus_;
    std::uint32_t jakso_ = 0;
    bool odottaa_ = false;
};

// @alku paateuart
// Sarjaportti, joka myös vastaanottaa. Rekisterit: 0x0 DATA (kirjoitus
// lähettää; luku palauttaa vastaanotetun merkin ja kuittaa
// keskeytyksen), 0x4 TILA (bitti 0: lähetin vapaana, bitti 1: merkki
// odottaa). Testipenkki syöttää merkit funktiolla vastaanota().
class Paateuart : public Uart {
public:
    sc_core::sc_out<bool> irq{"irq"};
    std::vector<sc_core::sc_time> nousut;
    std::vector<sc_core::sc_time> laskut;

    SC_HAS_PROCESS(Paateuart);
    explicit Paateuart(sc_core::sc_module_name nimi) : Uart(nimi) {
        SC_METHOD(linja);
        sensitive << saapui_ << luettu_;
        dont_initialize();
    }

    void vastaanota(char merkki) {
        merkki_ = static_cast<unsigned char>(merkki);
        saapui_.notify(sc_core::SC_ZERO_TIME);
    }

protected:
    Tila lue(sc_dt::uint64 osoite, std::uint32_t& arvo,
             const sc_core::sc_time& aika) override {
        if (osoite == 0x0) {
            arvo = merkki_;
            luettu_.notify(aika - sc_core::sc_time_stamp());
            return tlm::TLM_OK_RESPONSE;
        }
        if (osoite == 0x4) {
            arvo = 1u | (odottaa_ ? 2u : 0u);
            return tlm::TLM_OK_RESPONSE;
        }
        return tlm::TLM_ADDRESS_ERROR_RESPONSE;
    }

private:
    void linja() {
        if (luettu_.triggered() && odottaa_) {
            odottaa_ = false;
            laskut.push_back(sc_core::sc_time_stamp());
        }
        if (saapui_.triggered()) {
            odottaa_ = true;
            nousut.push_back(sc_core::sc_time_stamp());
        }
        irq.write(odottaa_);
    }

    sc_core::sc_event saapui_, luettu_;
    std::uint32_t merkki_ = 0;
    bool odottaa_ = false;
};
// @loppu paateuart
