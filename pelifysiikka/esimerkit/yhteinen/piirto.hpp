// Pieni ohjelmistorenderöijä kuvitusta ja vianetsintää varten:
// kolmiot syvyyspuskurilla ja tasavarjostuksella sekä viivat.
// Periaatteet ovat taidossa Renderöinnin perusteet; tässä toteutus on
// pidetty niin pienenä kuin kuvien tuottaminen sallii.
#pragma once
#include "vektori.hpp"

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <limits>
#include <string>
#include <vector>

// Kuvitus käännetään suuremmalla arvolla, jolloin sama kohtaus
// piirtyy tarkempana. Kuvan mittasuhteet eivät muutu.
#ifndef KUVAN_SUURENNOS
#define KUVAN_SUURENNOS 1
#endif

struct Vari {
    std::uint8_t r = 0, g = 0, b = 0;
};
inline Vari himmenna(Vari v, double k) {
    auto f = [k](std::uint8_t c) {
        return static_cast<std::uint8_t>(std::clamp(c * k, 0.0, 255.0));
    };
    return {f(v.r), f(v.g), f(v.b)};
}

// @alku kuva
class Kuva {
public:
    Kuva(int leveys, int korkeus, Vari tausta)
        : leveys_(leveys * KUVAN_SUURENNOS),
          korkeus_(korkeus * KUVAN_SUURENNOS),
          rgb_(static_cast<std::size_t>(leveys_) * korkeus_ * 3),
          syvyys_(static_cast<std::size_t>(leveys_) * korkeus_,
                  std::numeric_limits<double>::infinity()) {
        for (int y = 0; y < korkeus_; ++y)  // taivas vaalenee alaspäin
            for (int x = 0; x < leveys_; ++x)
                aseta(x, y, himmenna(tausta, 0.8 + 0.2 * y / korkeus_));
    }
    int leveys() const { return leveys_; }
    int korkeus() const { return korkeus_; }
    // Piirtää pikselin, jos se on lähempänä kuin aiemmin piirretty.
    void pikseli(int x, int y, double z, Vari v) {
        if (x < 0 || y < 0 || x >= leveys_ || y >= korkeus_) return;
        auto i = static_cast<std::size_t>(y) * leveys_ + x;
        if (z >= syvyys_[i]) return;
        syvyys_[i] = z;
        aseta(x, y, v);
    }
    void tallenna_ppm(const std::string& polku) const {
        std::ofstream f(polku, std::ios::binary);
        f << "P6\n" << leveys_ << " " << korkeus_ << "\n255\n";
        f.write(reinterpret_cast<const char*>(rgb_.data()),
                static_cast<std::streamsize>(rgb_.size()));
    }

private:
    void aseta(int x, int y, Vari v) {
        auto i = (static_cast<std::size_t>(y) * leveys_ + x) * 3;
        rgb_[i] = v.r;
        rgb_[i + 1] = v.g;
        rgb_[i + 2] = v.b;
    }
    int leveys_, korkeus_;
    std::vector<std::uint8_t> rgb_;
    std::vector<double> syvyys_;
};
// @loppu kuva

// @alku piirtaja
// Piirtää maailmakoordinaateissa annettuja kolmioita ja viivoja.
class Piirtaja {
public:
    Piirtaja(Kuva& kuva, const Mat4& nakyma_projektio)
        : kuva_(kuva), np_(nakyma_projektio) {}

    void kolmio(Vec3 a, Vec3 b, Vec3 c, Vari vari) {
        Vec3 n = risti(b - a, c - a);
        double p = pituus(n);
        if (p < 1e-12) return;
        double valo = 0.4 + 0.6 * std::max(0.0, piste(n, valo_) / p);
        vari = himmenna(vari, valo);
        // Leikkaus lähitasoon: kärjet, joilla w on liian pieni, korvataan
        // reunan ja tason leikkauspisteillä.
        Vec4 sisaan[3] = {np_ * Vec4{a.x, a.y, a.z, 1},
                          np_ * Vec4{b.x, b.y, b.z, 1},
                          np_ * Vec4{c.x, c.y, c.z, 1}};
        Vec4 ulos[4];
        int n_ulos = 0;
        for (int i = 0; i < 3; ++i) {
            Vec4 p0 = sisaan[i], p1 = sisaan[(i + 1) % 3];
            bool s0 = p0.w > LAHI, s1 = p1.w > LAHI;
            if (s0) ulos[n_ulos++] = p0;
            if (s0 != s1) {
                double t = (LAHI - p0.w) / (p1.w - p0.w);
                ulos[n_ulos++] = {p0.x + t * (p1.x - p0.x),
                                  p0.y + t * (p1.y - p0.y),
                                  p0.z + t * (p1.z - p0.z), LAHI};
            }
        }
        for (int i = 1; i + 1 < n_ulos; ++i)
            rasteroi(ruudulle(ulos[0]), ruudulle(ulos[i]),
                     ruudulle(ulos[i + 1]), vari);
    }

    // Viiva piirretään hieman pintojen eteen, jotta se näkyy pinnalla.
    // paalle = true ohittaa syvyystestin (vianetsintäviivat).
    void viiva(Vec3 a, Vec3 b, Vari vari, bool paalle = false) {
        Vec4 p0 = np_ * Vec4{a.x, a.y, a.z, 1};
        Vec4 p1 = np_ * Vec4{b.x, b.y, b.z, 1};
        if (p0.w <= LAHI && p1.w <= LAHI) return;
        if (p0.w <= LAHI) std::swap(p0, p1);
        if (p1.w <= LAHI) {
            double t = (LAHI - p0.w) / (p1.w - p0.w);
            p1 = {p0.x + t * (p1.x - p0.x), p0.y + t * (p1.y - p0.y),
                  p0.z + t * (p1.z - p0.z), LAHI};
        }
        Vec3 s0 = ruudulle(p0), s1 = ruudulle(p1);
        int askelia = static_cast<int>(
            std::max(std::abs(s1.x - s0.x), std::abs(s1.y - s0.y))) + 1;
        if (askelia > 4 * (kuva_.leveys() + kuva_.korkeus())) return;
        for (int i = 0; i <= askelia; ++i) {
            Vec3 p = lerp(s0, s1, static_cast<double>(i) / askelia);
            double z = paalle ? -2.0 : p.z - 0.002;
            int x = static_cast<int>(p.x), y = static_cast<int>(p.y);
            for (int dy = 0; dy < 2 * KUVAN_SUURENNOS; ++dy)  // paksuus
                for (int dx = 0; dx < 2 * KUVAN_SUURENNOS; ++dx)
                    kuva_.pikseli(x + dx, y + dy, z, vari);
        }
    }

    Vec3 valo_ = normalisoi(Vec3{0.4, 1.0, 0.6});  // suunta kohti valoa

private:
    static constexpr double LAHI = 0.05;

    Vec3 ruudulle(Vec4 p) const {  // perspektiivijako ja näkymämuunnos
        return {(p.x / p.w * 0.5 + 0.5) * kuva_.leveys(),
                (0.5 - p.y / p.w * 0.5) * kuva_.korkeus(), p.z / p.w};
    }
    void rasteroi(Vec3 a, Vec3 b, Vec3 c, Vari vari) {
        double ala = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
        if (std::abs(ala) < 1e-12) return;
        int x0 = std::max(0, static_cast<int>(std::min({a.x, b.x, c.x})));
        int x1 = std::min(kuva_.leveys() - 1,
                          static_cast<int>(std::max({a.x, b.x, c.x})));
        int y0 = std::max(0, static_cast<int>(std::min({a.y, b.y, c.y})));
        int y1 = std::min(kuva_.korkeus() - 1,
                          static_cast<int>(std::max({a.y, b.y, c.y})));
        for (int y = y0; y <= y1; ++y)
            for (int x = x0; x <= x1; ++x) {
                double px = x + 0.5, py = y + 0.5;
                double wa = ((b.x - px) * (c.y - py) -
                             (b.y - py) * (c.x - px)) / ala;
                double wb = ((c.x - px) * (a.y - py) -
                             (c.y - py) * (a.x - px)) / ala;
                double wc = 1 - wa - wb;
                if (wa < 0 || wb < 0 || wc < 0) continue;
                kuva_.pikseli(x, y, wa * a.z + wb * b.z + wc * c.z, vari);
            }
    }
    Kuva& kuva_;
    Mat4 np_;
};
// @loppu piirtaja
