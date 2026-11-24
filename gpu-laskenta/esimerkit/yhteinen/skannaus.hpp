// Monitasoinen poissulkeva prefiksisumma GPU:lla (Blelloch).
#pragma once

#include "laskenta.hpp"

#include <memory>

// @alku skannaus
// Skannaa annetun puskurin paikallaan. Taso 0 skannaa 512 alkion
// lohkot ja kirjoittaa lohkojen summat; summat skannataan samalla
// tavalla rekursiivisesti, ja lopuksi kunkin lohkon alkioihin lisätään
// sitä edeltävien lohkojen summa. Kuvaajajoukot luodaan kerran, joten
// samaa oliota voi käyttää monta kertaa (esim. lajittelun kierroksilla).
class Skannaus {
public:
    Skannaus(const VkYmparisto& vk, Puskuri<std::uint32_t>& data)
        : lohko_(vk, "bin/skannaus_lohko.spv", 2, 4),
          lisaa_(vk, "bin/skannaus_lisaa.spv", 2, 4) {
        Puskuri<std::uint32_t>* taso = &data;
        while (true) {
            const std::uint32_t n =
                static_cast<std::uint32_t>(taso->koko());
            const std::uint32_t r = ryhmia(n, 512);
            summat_.push_back(
                std::make_unique<Puskuri<std::uint32_t>>(vk, r));
            auto& s = *summat_.back();
            tasot_.push_back({n, r, lohko_.joukko({taso->puskuri,
                                                   s.puskuri}),
                              lisaa_.joukko({taso->puskuri, s.puskuri})});
            if (r == 1) {
                break;
            }
            taso = &s;
        }
    }

    // Tallentaa skannauksen komentopuskuriin ja palauttaa ajojen määrän.
    int tallenna(VkCommandBuffer kp) const {
        int ajoja = 0;
        for (const Taso& t : tasot_) {           // lohkot ylös
            lohko_.aja(kp, t.lohko, t.n, {t.ryhmat});
            laskentaeste(kp);
            ++ajoja;
        }
        for (std::size_t k = tasot_.size() - 1; k-- > 0;) {
            const Taso& t = tasot_[k];           // summat alas
            lisaa_.aja(kp, t.lisaa, t.n, {t.ryhmat});
            laskentaeste(kp);
            ++ajoja;
        }
        return ajoja;
    }
    std::size_t tasoja() const { return tasot_.size(); }

private:
    struct Taso {
        std::uint32_t n, ryhmat;
        VkDescriptorSet lohko, lisaa;
    };
    Putki lohko_, lisaa_;
    std::vector<std::unique_ptr<Puskuri<std::uint32_t>>> summat_;
    std::vector<Taso> tasot_;
};
// @loppu skannaus
