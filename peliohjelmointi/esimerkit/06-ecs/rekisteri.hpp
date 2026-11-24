// Pieni entiteettikomponenttijärjestelmä (ECS) harvoilla joukoilla.
#pragma once
#include <cassert>
#include <cstdint>
#include <limits>
#include <memory>
#include <tuple>
#include <typeindex>
#include <unordered_map>
#include <vector>

// @alku entiteetti
// Entiteetti on pelkkä tunniste: indeksi ja sukupolvi. Sukupolvi
// kasvaa, kun indeksi kierrätetään, joten vanha tunniste ei osoita
// uuteen entiteettiin.
struct Entiteetti {
    std::uint32_t indeksi;
    std::uint32_t sukupolvi;
    bool operator==(const Entiteetti&) const = default;
};
// @loppu entiteetti

// @alku joukko
// Harva joukko: komponentit tiiviisti taulukossa (tiheä), ja harva
// taulukko kertoo entiteetin indeksistä komponentin paikan.
class JoukkoPohja {
public:
    virtual ~JoukkoPohja() = default;
    virtual void poista(std::uint32_t indeksi) = 0;
};

template <typename T>
class Joukko : public JoukkoPohja {
public:
    static constexpr auto EI = std::numeric_limits<std::uint32_t>::max();

    T& lisaa(std::uint32_t e, T arvo) {
        if (e >= harva_.size()) {
            harva_.resize(e + 1, EI);
        }
        harva_[e] = static_cast<std::uint32_t>(tihea_.size());
        tihea_.push_back(e);
        arvot_.push_back(std::move(arvo));
        return arvot_.back();
    }
    T* hae(std::uint32_t e) {
        return e < harva_.size() && harva_[e] != EI ? &arvot_[harva_[e]]
                                                     : nullptr;
    }
    // Poisto siirtää viimeisen alkion aukkoon: taulukko pysyy tiiviinä.
    void poista(std::uint32_t e) override {
        if (hae(e) == nullptr) {
            return;
        }
        const std::uint32_t paikka = harva_[e];
        const std::uint32_t viimeinen = tihea_.back();
        tihea_[paikka] = viimeinen;
        arvot_[paikka] = std::move(arvot_.back());
        harva_[viimeinen] = paikka;
        tihea_.pop_back();
        arvot_.pop_back();
        harva_[e] = EI;
    }
    const std::vector<std::uint32_t>& entiteetit() const { return tihea_; }
    std::vector<T>& arvot() { return arvot_; }

private:
    std::vector<std::uint32_t> harva_;  // indeksi -> paikka tiheässä
    std::vector<std::uint32_t> tihea_;  // paikka -> indeksi
    std::vector<T> arvot_;              // samassa järjestyksessä
};
// @loppu joukko

// @alku rekisteri
class Rekisteri {
public:
    Entiteetti luo() {
        if (!vapaat_.empty()) {
            const std::uint32_t i = vapaat_.back();
            vapaat_.pop_back();
            return {i, sukupolvet_[i]};
        }
        sukupolvet_.push_back(0);
        return {static_cast<std::uint32_t>(sukupolvet_.size() - 1), 0};
    }
    bool elossa(Entiteetti e) const {
        return e.indeksi < sukupolvet_.size() &&
               sukupolvet_[e.indeksi] == e.sukupolvi;
    }
    void tuhoa(Entiteetti e) {
        assert(elossa(e));
        for (auto& [tyyppi, joukko] : joukot_) {
            joukko->poista(e.indeksi);
        }
        ++sukupolvet_[e.indeksi];
        vapaat_.push_back(e.indeksi);
    }
    template <typename T>
    T& lisaa(Entiteetti e, T arvo) {
        return joukko<T>().lisaa(e.indeksi, std::move(arvo));
    }
    template <typename T>
    T* hae(Entiteetti e) {
        return elossa(e) ? joukko<T>().hae(e.indeksi) : nullptr;
    }
    // Käy läpi entiteetit, joilla on kaikki pyydetyt komponentit.
    // Iteroidaan ensimmäisen tyypin tiheää taulukkoa.
    template <typename Eka, typename... Muut, typename F>
    void kaikille(F&& f) {
        auto& eka = joukko<Eka>();
        const auto& idt = eka.entiteetit();
        for (std::size_t i = 0; i < idt.size(); ++i) {
            [[maybe_unused]] const std::uint32_t e = idt[i];
            auto muut = std::tuple{joukko<Muut>().hae(e)...};
            const bool kaikki = std::apply(
                [](auto*... p) { return ((p != nullptr) && ...); }, muut);
            if (kaikki) {
                std::apply([&](auto*... p) { f(eka.arvot()[i], *p...); },
                           muut);
            }
        }
    }

private:
    template <typename T>
    Joukko<T>& joukko() {
        auto& p = joukot_[std::type_index(typeid(T))];
        if (!p) {
            p = std::make_unique<Joukko<T>>();
        }
        return static_cast<Joukko<T>&>(*p);
    }

    std::vector<std::uint32_t> sukupolvet_;
    std::vector<std::uint32_t> vapaat_;
    std::unordered_map<std::type_index, std::unique_ptr<JoukkoPohja>>
        joukot_;
};
// @loppu rekisteri
