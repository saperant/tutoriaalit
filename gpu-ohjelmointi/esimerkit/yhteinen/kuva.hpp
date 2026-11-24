// Kuva RGBA8-pikseleinä: pikselien luku, raportit ja PPM-tallennus.
#pragma once

#include <array>
#include <cstdint>
#include <format>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Kuva {
    int leveys = 0;
    int korkeus = 0;
    std::vector<std::uint8_t> rgba;  // rivit ylhäältä alas

    Kuva(int l, int k)
        : leveys{l}, korkeus{k},
          rgba(static_cast<std::size_t>(l * k * 4)) {}

    // Pikselin (x, y) arvot; y kasvaa alaspäin kuten kuvatiedostoissa.
    std::array<int, 4> pikseli(int x, int y) const {
        const auto i = static_cast<std::size_t>((y * leveys + x) * 4);
        return {rgba[i], rgba[i + 1], rgba[i + 2], rgba[i + 3]};
    }

    // Esim. "(255, 0, 0)": väri ilman alfaa raportteihin.
    std::string vari(int x, int y) const {
        const auto p = pikseli(x, y);
        return std::format("({}, {}, {})", p[0], p[1], p[2]);
    }

    // Kuinka moni pikseli poikkeaa annetusta taustasta.
    int peitetyt(std::array<int, 3> tausta) const {
        int n = 0;
        for (int y = 0; y < korkeus; ++y) {
            for (int x = 0; x < leveys; ++x) {
                const auto p = pikseli(x, y);
                if (p[0] != tausta[0] || p[1] != tausta[1] ||
                    p[2] != tausta[2]) {
                    ++n;
                }
            }
        }
        return n;
    }

    // Binäärinen PPM (P6): yksinkertainen, jokainen kuvaohjelma lukee.
    void tallenna_ppm(const std::string& polku) const {
        std::ofstream ulos(polku, std::ios::binary);
        if (!ulos) {
            throw std::runtime_error("ei voi kirjoittaa: " + polku);
        }
        ulos << std::format("P6\n{} {}\n255\n", leveys, korkeus);
        for (std::size_t i = 0; i < rgba.size(); i += 4) {
            ulos.write(reinterpret_cast<const char*>(&rgba[i]), 3);
        }
    }
};
