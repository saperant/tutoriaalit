// Sprite-atlas ja ruutuanimaatio.
#pragma once
#include "kuva.hpp"

#include <vector>

// @alku animaatio
// Animaatio on lista atlaksen alueita ja yhden kuvan kesto. Kuva
// valitaan pelin ajasta, ei piirtokerroista, joten animaation nopeus
// ei riipu ruudunpäivitysnopeudesta.
struct Animaatio {
    std::vector<Alue> kuvat;
    double kuvan_kesto = 0.1;  // sekuntia
    bool toistuva = true;

    const Alue& kuva(double aika) const {
        auto i = static_cast<std::size_t>(aika / kuvan_kesto);
        i = toistuva ? i % kuvat.size()
                     : std::min(i, kuvat.size() - 1);
        return kuvat[i];
    }
};
// @loppu animaatio
