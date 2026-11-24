// Kuvapuskuri, värit ja tiedostomuoto PPM.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

// @alku vari
// Valon määrä lineaarisena: 0 = ei valoa, 1 = näytön maksimi.
struct Vari {
    double r = 0, g = 0, b = 0;
};
inline Vari operator+(Vari a, Vari b) {
    return {a.r + b.r, a.g + b.g, a.b + b.b};
}
inline Vari operator*(Vari a, Vari b) {
    return {a.r * b.r, a.g * b.g, a.b * b.b};
}
inline Vari operator*(double k, Vari a) {
    return {k * a.r, k * a.g, k * a.b};
}

// Tallennettava pikseli: kolme tavua sRGB-koodattuna.
struct Rgb {
    std::uint8_t r = 0, g = 0, b = 0;
    bool operator==(const Rgb&) const = default;
};
// @loppu vari

// @alku srgb
// sRGB-siirtofunktio: lineaarinen 0..1 -> koodattu 0..1.
inline double srgb_koodaa(double v) {
    v = std::clamp(v, 0.0, 1.0);
    return v <= 0.0031308 ? 12.92 * v
                          : 1.055 * std::pow(v, 1.0 / 2.4) - 0.055;
}
inline double srgb_pura(double s) {
    return s <= 0.04045 ? s / 12.92
                        : std::pow((s + 0.055) / 1.055, 2.4);
}
inline std::uint8_t tavuksi(double s) {
    return static_cast<std::uint8_t>(
        std::lround(std::clamp(s, 0.0, 1.0) * 255.0));
}
inline Rgb koodaa(Vari v) {
    return {tavuksi(srgb_koodaa(v.r)), tavuksi(srgb_koodaa(v.g)),
            tavuksi(srgb_koodaa(v.b))};
}
inline Vari pura(Rgb c) {
    return {srgb_pura(c.r / 255.0), srgb_pura(c.g / 255.0),
            srgb_pura(c.b / 255.0)};
}
// @loppu srgb

// @alku kuva
class Kuva {
public:
    Kuva(int leveys, int korkeus, Rgb tausta = {})
        : l_(leveys), k_(korkeus),
          pikselit_(static_cast<std::size_t>(leveys) * korkeus,
                    tausta) {}
    int leveys() const { return l_; }
    int korkeus() const { return k_; }
    // Rivi kerrallaan ylhäältä alas: indeksi y * leveys + x.
    Rgb& operator()(int x, int y) {
        return pikselit_[static_cast<std::size_t>(y) * l_ + x];
    }
    Rgb operator()(int x, int y) const {
        return pikselit_[static_cast<std::size_t>(y) * l_ + x];
    }
    void aseta(int x, int y, Rgb c) {
        if (x >= 0 && x < l_ && y >= 0 && y < k_) (*this)(x, y) = c;
    }
    const std::vector<Rgb>& pikselit() const { return pikselit_; }

private:
    int l_, k_;
    std::vector<Rgb> pikselit_;
};

// Binäärinen PPM (P6): otsikko tekstinä, sitten RGB-tavut.
inline void tallenna_ppm(const Kuva& kuva, const std::string& nimi) {
    std::ofstream f(nimi, std::ios::binary);
    f << "P6\n" << kuva.leveys() << ' ' << kuva.korkeus() << "\n255\n";
    for (Rgb c : kuva.pikselit()) {
        f.put(static_cast<char>(c.r));
        f.put(static_cast<char>(c.g));
        f.put(static_cast<char>(c.b));
    }
}
// @loppu kuva

// @alku summa
// FNV-1a-tiiviste kuvan tavuista: yksikin muuttunut pikseli näkyy.
inline std::uint32_t tarkistussumma(const Kuva& kuva) {
    std::uint32_t h = 2166136261u;
    auto lisaa = [&h](std::uint8_t tavu) {
        h ^= tavu;
        h *= 16777619u;
    };
    for (Rgb c : kuva.pikselit()) {
        lisaa(c.r);
        lisaa(c.g);
        lisaa(c.b);
    }
    return h;
}

// Kirkkaus 0..255 sRGB-tavuista (Rec. 709 -painot, likimäärin).
inline int kirkkaus(Rgb c) {
    return (2126 * c.r + 7152 * c.g + 722 * c.b + 5000) / 10000;
}

// Tarkistussumma, peitto ja keskikirkkaus yhdelle riville.
inline void tilasto(const char* nimi, const Kuva& kuva, Rgb tausta = {}) {
    long peitetty = 0, summa = 0;
    for (Rgb c : kuva.pikselit()) {
        if (!(c == tausta)) ++peitetty;
        summa += kirkkaus(c);
    }
    long n = static_cast<long>(kuva.pikselit().size());
    int merkit = 0;  // UTF-8: jatkotavut eivät ole uusia merkkejä
    for (const char* c = nimi; *c; ++c) merkit += (*c & 0xC0) != 0x80;
    std::printf("%s%*s summa %08x  peitto %5ld/%ld  kirkkaus %ld\n",
                nimi, std::max(0, 14 - merkit), "", tarkistussumma(kuva),
                peitetty, n, (summa + n / 2) / n);
}
// @loppu summa

// @alku ascii
// Pienennetty esikatselu tekstinä: jokainen merkki on lohkon
// keskikirkkaus. Merkit tummasta vaaleaan.
inline void ascii(const Kuva& kuva, int lohko_x, int lohko_y) {
    const char* asteikko = " .:-=+*#%@";
    for (int y0 = 0; y0 + lohko_y <= kuva.korkeus(); y0 += lohko_y) {
        std::string rivi;
        for (int x0 = 0; x0 + lohko_x <= kuva.leveys(); x0 += lohko_x) {
            int s = 0;
            for (int y = y0; y < y0 + lohko_y; ++y)
                for (int x = x0; x < x0 + lohko_x; ++x)
                    s += kirkkaus(kuva(x, y));
            int ka = s / (lohko_x * lohko_y);
            rivi += asteikko[ka * 10 / 256];
        }
        while (!rivi.empty() && rivi.back() == ' ') rivi.pop_back();
        std::printf("|%s\n", rivi.c_str());
    }
}
// @loppu ascii
