// Yksinkertainen sarjaportti: lähetetyt merkit tulostetaan riveittäin.
#pragma once
#include <iostream>
#include <string>

#include "rekisterit.hpp"

// @alku uart
// Rekisterit: 0x0 DATA (kirjoitus lähettää merkin), 0x4 TILA (bitti 0:
// lähetin vapaana). Malli ei mallinna siirtonopeutta, joten lähetin on
// aina vapaana.
class Uart : public Rekisterilohko {
public:
    explicit Uart(sc_core::sc_module_name nimi)
        : Rekisterilohko(nimi, sc_core::sc_time(20, sc_core::SC_NS)) {}

protected:
    Tila lue(sc_dt::uint64 osoite, std::uint32_t& arvo,
             const sc_core::sc_time&) override {
        if (osoite != 0x4) {
            return tlm::TLM_ADDRESS_ERROR_RESPONSE;
        }
        arvo = 1;
        return tlm::TLM_OK_RESPONSE;
    }

    Tila kirjoita(sc_dt::uint64 osoite, std::uint32_t arvo,
                  const sc_core::sc_time& aika) override {
        if (osoite != 0x0) {
            return tlm::TLM_ADDRESS_ERROR_RESPONSE;
        }
        const char merkki = static_cast<char>(arvo & 0xFF);
        if (merkki == '\n') {
            std::cout << "[uart " << aika << "] " << rivi_ << '\n';
            rivi_.clear();
        } else {
            rivi_ += merkki;
        }
        return tlm::TLM_OK_RESPONSE;
    }

private:
    std::string rivi_;
};
// @loppu uart
