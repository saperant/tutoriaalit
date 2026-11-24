// Generic payloadien muistinhallinta AT-mallinnukseen.
#pragma once
#include <memory>
#include <vector>

#include <tlm>

// @alku mm
// AT-tyylissä transaktio elää usean funktiokutsun yli, joten sen
// omistus hoidetaan viitelaskennalla: jokainen osapuoli, joka tallentaa
// transaktion, kutsuu acquire(), ja luopuessaan release(). Kun laskuri
// menee nollaan, payload palaa tähän pooliin.
class Muistinhallinta : public tlm::tlm_mm_interface {
public:
    tlm::tlm_generic_payload* varaa() {
        if (vapaat_.empty()) {
            kaikki_.push_back(
                std::make_unique<tlm::tlm_generic_payload>(this));
            vapaat_.push_back(kaikki_.back().get());
        }
        tlm::tlm_generic_payload* gp = vapaat_.back();
        vapaat_.pop_back();
        return gp;
    }

    void free(tlm::tlm_generic_payload* gp) override {
        gp->reset();  // tyhjentää myös laajennukset
        vapaat_.push_back(gp);
    }

private:
    std::vector<std::unique_ptr<tlm::tlm_generic_payload>> kaikki_;
    std::vector<tlm::tlm_generic_payload*> vapaat_;
};
// @loppu mm
