// Rajallinen FIFO-jono omana primitiivikanavana.
#pragma once
#include <cstddef>
#include <deque>
#include <systemc>

// @alku rajapinnat
// Kanavan rajapinnat: portti sc_port<JonoKirjoitus<T>> näkee vain
// kirjoitusmetodit, sc_port<JonoLuku<T>> vain lukumetodit.
template <typename T>
struct JonoKirjoitus : virtual sc_core::sc_interface {
    virtual void kirjoita(const T& arvo) = 0;  // odottaa tilaa
};

template <typename T>
struct JonoLuku : virtual sc_core::sc_interface {
    virtual T lue() = 0;                       // odottaa dataa
    virtual std::size_t maara() const = 0;     // luettavissa nyt
};
// @loppu rajapinnat

// @alku kanava
// Jono noudattaa signaalin tapaa: kirjoitettu alkio näkyy lukijalle ja
// vapautunut paikka kirjoittajalle vasta päivitysvaiheen jälkeen. Siksi
// tulos ei riipu siitä, kumpi prosessi ajetaan delta-syklissä ensin.
template <typename T>
class Jono : public sc_core::sc_prim_channel,
             public JonoKirjoitus<T>,
             public JonoLuku<T> {
public:
    Jono(const char* nimi, std::size_t koko)
        : sc_core::sc_prim_channel(nimi), koko_(koko) {}

    void kirjoita(const T& arvo) override {
        while (puskuri_.size() + poistetut_ >= koko_) {
            sc_core::wait(luettu_);
        }
        puskuri_.push_back(arvo);
        ++uudet_;
        request_update();
    }

    T lue() override {
        while (maara() == 0) {
            sc_core::wait(kirjoitettu_);
        }
        T arvo = puskuri_.front();
        puskuri_.pop_front();
        ++poistetut_;
        request_update();
        return arvo;
    }

    std::size_t maara() const override {
        return puskuri_.size() - uudet_;
    }

private:
    // Päivitysvaihe: muutokset näkyviin ja odottajat herätetään.
    void update() override {
        if (uudet_ > 0) {
            uudet_ = 0;
            kirjoitettu_.notify(sc_core::SC_ZERO_TIME);
        }
        if (poistetut_ > 0) {
            poistetut_ = 0;
            luettu_.notify(sc_core::SC_ZERO_TIME);
        }
    }

    std::size_t koko_;
    std::deque<T> puskuri_;
    std::size_t uudet_ = 0;      // kirjoitettu tässä delta-syklissä
    std::size_t poistetut_ = 0;  // luettu tässä delta-syklissä
    sc_core::sc_event kirjoitettu_, luettu_;
};
// @loppu kanava
