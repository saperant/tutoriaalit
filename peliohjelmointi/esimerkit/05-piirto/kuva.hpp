// Ohjelmistorenderöinnin perusosat: kuvapuskuri, alueet ja spritet.
#pragma once
#include <cstdint>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

// @alku kuva
struct Vari {
    std::uint8_t r = 0, g = 0, b = 0, a = 255;
    bool operator==(const Vari&) const = default;
};

struct Alue {  // suorakulmio pikseleinä
    int x = 0, y = 0, w = 0, h = 0;
};

class Kuva {
public:
    Kuva(int leveys, int korkeus, Vari tausta = {});
    int leveys() const { return leveys_; }
    int korkeus() const { return korkeus_; }
    Vari& operator()(int x, int y) { return pikselit_[y * leveys_ + x]; }
    const Vari& operator()(int x, int y) const {
        return pikselit_[y * leveys_ + x];
    }
    void tayta(Alue alue, Vari vari);  // leikataan kuvan rajoihin
    void tallenna_ppm(const std::string& polku) const;
    std::uint32_t tarkistussumma() const;

private:
    int leveys_, korkeus_;
    std::vector<Vari> pikselit_;  // rivi kerrallaan, vasemmalta oikealle
};
// @loppu kuva

// Piirtää lähteen alueen kohteeseen kohtaan (x, y). Läpinäkyvät
// pikselit ohitetaan; peilaus kääntää spriten vaakasuunnassa.
void piirra(Kuva& kohde, const Kuva& lahde, Alue alue, int x, int y,
            bool peilaa = false);

// Kuva ASCII-taiteesta: paletti kertoo merkin värin, '.' on läpinäkyvä.
using Paletti = std::span<const std::pair<char, Vari>>;
Kuva ascii_kuvaksi(std::span<const std::string_view> rivit, Paletti p);
