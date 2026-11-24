// FIR-kiihdytin TLM-oheislaitteena: rekisterit ja DMA.
#pragma once
#include <array>
#include <cstdint>
#include <cstring>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/simple_target_socket.h>

constexpr int TAPIT = 16;
constexpr std::array<std::int32_t, TAPIT> KERTOIMET = {
    1, -2, 3, -4, 5, -6, 7, 8, 8, 7, -6, 5, -4, 3, -2, 1};

// @alku fir
// Sama suodin ohjelmistona ja kiihdyttimessä: y[i] = sum h[j] x[i-j],
// ja näytteet ennen alkua ovat nollia.
inline std::int32_t fir(const std::int32_t* x, int i) {
    std::int32_t y = 0;
    for (int j = 0; j < TAPIT && j <= i; ++j) y += KERTOIMET[j] * x[i - j];
    return y;
}
// @loppu fir

// @alku rekisterit
// Rekisterikartta (siirtymä tavuina): 0 LAHDE, 4 KOHDE, 8 PITUUS
// (näytettä), 12 KASKY (1 = aloita). Valmistuminen ilmoitetaan
// keskeytyksellä (tapahtuma valmis).
class Kiihdytin : public sc_core::sc_module {
public:
    tlm_utils::simple_target_socket<Kiihdytin> rekisterit{"rekisterit"};
    tlm_utils::simple_initiator_socket<Kiihdytin> dma{"dma"};
    sc_core::sc_event valmis;

    SC_HAS_PROCESS(Kiihdytin);
    explicit Kiihdytin(sc_core::sc_module_name nimi) : sc_module(nimi) {
        rekisterit.register_b_transport(this, &Kiihdytin::b_transport);
        SC_THREAD(aja);
    }
    // @loppu rekisterit

private:
    static constexpr int PALA = 16;  // näytettä yhdessä DMA-siirrossa
    const sc_core::sc_time rekisteri_{2, sc_core::SC_NS};
    const sc_core::sc_time purske_{8, sc_core::SC_NS};  // 64 B, 8 B/ns
    const sc_core::sc_time jakso_{1, sc_core::SC_NS};

    void b_transport(tlm::tlm_generic_payload& gp, sc_core::sc_time& t) {
        std::uint32_t arvo = 0;
        std::memcpy(&arvo, gp.get_data_ptr(), 4);
        const auto i = static_cast<std::size_t>(gp.get_address() / 4);
        if (gp.is_write() && i < 3) {
            rek_[i] = arvo;
        } else if (gp.is_write() && i == 3 && arvo == 1) {
            aloita_.notify(t + rekisteri_);  // annotoitu aika
        }
        t += rekisteri_;
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
    }

    // @alku dma
    // Purske: yksi DMA-siirto väylän läpi. Väylä ja muisti lisäävät
    // viiveensä, purske lisää siirtoajan.
    void siirra(tlm::tlm_command komento, std::uint32_t osoite,
                std::int32_t* data) {
        tlm::tlm_generic_payload gp;
        gp.set_command(komento);
        gp.set_address(osoite);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(data));
        gp.set_data_length(4 * PALA);
        gp.set_streaming_width(4 * PALA);
        gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
        sc_core::sc_time t = purske_;
        dma->b_transport(gp, t);
        if (gp.is_response_error()) {
            SC_REPORT_ERROR("Kiihdytin", gp.get_response_string().c_str());
        }
        wait(t);
    }

    // Ei kaksoispuskurointia: lue pala, laske (1 näyte/jakso), kirjoita.
    void aja() {
        for (;;) {
            wait(aloita_);
            const auto [lahde, kohde, pituus] = rek_;
            std::array<std::int32_t, PALA + TAPIT> x{};  // edelliset tapit
            std::array<std::int32_t, PALA> y{};
            for (std::uint32_t alku = 0; alku < pituus; alku += PALA) {
                std::memmove(x.data(), x.data() + PALA, 4 * TAPIT);
                siirra(tlm::TLM_READ_COMMAND, lahde + 4 * alku,
                       x.data() + TAPIT);
                laske(x, y);
                wait(PALA * jakso_);
                siirra(tlm::TLM_WRITE_COMMAND, kohde + 4 * alku, y.data());
            }
            wait(TAPIT * jakso_);  // liukuhihnan tyhjennys
            valmis.notify();
        }
    }
    // @loppu dma

    // Suodin palalle: x:n alussa ovat edellisen palan viimeiset
    // TAPIT näytettä (alussa nollia).
    static void laske(const std::array<std::int32_t, PALA + TAPIT>& x,
                      std::array<std::int32_t, PALA>& y) {
        for (int i = 0; i < PALA; ++i) {
            std::int32_t s = 0;
            for (int j = 0; j < TAPIT; ++j) {
                s += KERTOIMET[std::size_t(j)] *
                     x[std::size_t(TAPIT + i - j)];
            }
            y[std::size_t(i)] = s;
        }
    }

    std::array<std::uint32_t, 3> rek_{};
    sc_core::sc_event aloita_;
};
