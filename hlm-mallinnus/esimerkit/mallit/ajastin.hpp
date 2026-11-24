// Vapaasti juokseva ajastin: lukee aloittajan kelloa.
#pragma once
#include "rekisterit.hpp"

// @alku ajastin
// Rekisteri 0x0 LASKURI: kuluneet 100 MHz:n kellojaksot (10 ns).
// Aikatietoinen malli käyttää aloittajan paikallista aikaa
// (simulaatioaika + viive), naiivi pelkkää simulaatioaikaa, joka
// laahaa ajallisesti irrotetun aloittajan perässä.
class Ajastin : public Rekisterilohko {
public:
    Ajastin(sc_core::sc_module_name nimi, bool aikatietoinen = true)
        : Rekisterilohko(nimi, sc_core::sc_time(10, sc_core::SC_NS)),
          aikatietoinen_(aikatietoinen) {}

protected:
    Tila lue(sc_dt::uint64 osoite, std::uint32_t& arvo,
             const sc_core::sc_time& aika) override {
        if (osoite != 0x0) {
            return tlm::TLM_ADDRESS_ERROR_RESPONSE;
        }
        const sc_core::sc_time nyt =
            aikatietoinen_ ? aika : sc_core::sc_time_stamp();
        const sc_core::sc_time jakso(10, sc_core::SC_NS);
        arvo = static_cast<std::uint32_t>(nyt / jakso);
        return tlm::TLM_OK_RESPONSE;
    }

    Tila kirjoita(sc_dt::uint64, std::uint32_t,
                  const sc_core::sc_time&) override {
        return tlm::TLM_COMMAND_ERROR_RESPONSE;  // vain luettava
    }

private:
    bool aikatietoinen_;
};
// @loppu ajastin
