#include "kuva.hpp"

#include <algorithm>
#include <fstream>

Kuva::Kuva(int leveys, int korkeus, Vari tausta)
    : leveys_(leveys), korkeus_(korkeus),
      pikselit_(static_cast<std::size_t>(leveys * korkeus), tausta) {}

void Kuva::tayta(Alue a, Vari vari) {
    const int x0 = std::max(a.x, 0), x1 = std::min(a.x + a.w, leveys_);
    const int y0 = std::max(a.y, 0), y1 = std::min(a.y + a.h, korkeus_);
    for (int y = y0; y < y1; ++y) {
        for (int x = x0; x < x1; ++x) {
            (*this)(x, y) = vari;
        }
    }
}

void Kuva::tallenna_ppm(const std::string& polku) const {
    std::ofstream f(polku, std::ios::binary);
    f << "P6\n" << leveys_ << ' ' << korkeus_ << "\n255\n";
    for (const Vari& v : pikselit_) {
        f.put(static_cast<char>(v.r)).put(static_cast<char>(v.g))
            .put(static_cast<char>(v.b));
    }
}

std::uint32_t Kuva::tarkistussumma() const {
    std::uint32_t h = 2166136261u;  // FNV-1a
    for (const Vari& v : pikselit_) {
        for (std::uint8_t tavu : {v.r, v.g, v.b, v.a}) {
            h = (h ^ tavu) * 16777619u;
        }
    }
    return h;
}

// @alku piirra
void piirra(Kuva& kohde, const Kuva& lahde, Alue alue, int x, int y,
            bool peilaa) {
    for (int j = 0; j < alue.h; ++j) {
        const int ky = y + j;
        if (ky < 0 || ky >= kohde.korkeus()) {
            continue;  // leikkaus: rivi ruudun ulkopuolella
        }
        for (int i = 0; i < alue.w; ++i) {
            const int kx = x + i;
            if (kx < 0 || kx >= kohde.leveys()) {
                continue;
            }
            const int lx = alue.x + (peilaa ? alue.w - 1 - i : i);
            const Vari& v = lahde(lx, alue.y + j);
            if (v.a != 0) {  // tässä vain täysin peittävä tai läpinäkyvä
                kohde(kx, ky) = v;
            }
        }
    }
}
// @loppu piirra

Kuva ascii_kuvaksi(std::span<const std::string_view> rivit, Paletti p) {
    const int w = static_cast<int>(rivit.front().size());
    Kuva kuva(w, static_cast<int>(rivit.size()), Vari{0, 0, 0, 0});
    for (int y = 0; std::string_view rivi : rivit) {
        for (int x = 0; x < w; ++x) {
            for (const auto& [merkki, vari] : p) {
                if (rivi[static_cast<std::size_t>(x)] == merkki) {
                    kuva(x, y) = vari;
                }
            }
        }
        ++y;
    }
    return kuva;
}
