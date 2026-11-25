// Kipinän piirto ohjelmistona kuvapuskuriin (0xRRGGBB).
#pragma once
#include "peli.hpp"

#include <cstdint>
#include <string>
#include <vector>

struct Kuvapuskuri {
    static constexpr int W = 160, H = 120;
    std::vector<std::uint32_t> pikselit =
        std::vector<std::uint32_t>(W * H, 0);
    std::uint32_t tarkistussumma() const;
    void tallenna_ppm(const std::string& polku) const;
};

void piirra(const Peli& peli, Kuvapuskuri& kuva);
