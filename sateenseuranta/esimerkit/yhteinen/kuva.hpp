// Värit, liukulukukehys (HDR), sRGB-koodaus ja kuvien vertailu.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

// @alku vari
// Radianssi kolmella aallonpituuskaistalla (lineaarinen, ei rajaa 1).
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
inline double suurin(Vari a) { return std::max({a.r, a.g, a.b}); }
// Suhteellinen luminanssi (Rec. 709 -painot).
inline double luminanssi(Vari a) {
    return 0.2126 * a.r + 0.7152 * a.g + 0.0722 * a.b;
}
// @loppu vari

// @alku kehys
// Liukulukukuva: pikselin arvo on keskimääräinen radianssi.
class Kehys {
public:
    Kehys(int leveys, int korkeus)
        : l_(leveys), k_(korkeus),
          p_(static_cast<std::size_t>(leveys) * korkeus) {}
    int leveys() const { return l_; }
    int korkeus() const { return k_; }
    Vari& operator()(int x, int y) {
        return p_[static_cast<std::size_t>(y) * l_ + x];
    }
    Vari operator()(int x, int y) const {
        return p_[static_cast<std::size_t>(y) * l_ + x];
    }
    const std::vector<Vari>& pikselit() const { return p_; }

private:
    int l_, k_;
    std::vector<Vari> p_;
};
// @loppu kehys

// @alku srgb
// Lineaarinen arvo 0..1 sRGB-tavuksi (luku Kuvat ja pikselit
// renderöinnin perusteissa). Yli 1 menevä valo leikataan.
inline std::uint8_t srgb_tavu(double v) {
    v = std::clamp(v, 0.0, 1.0);
    double s = v <= 0.0031308 ? 12.92 * v
                              : 1.055 * std::pow(v, 1.0 / 2.4) - 0.055;
    return static_cast<std::uint8_t>(std::lround(s * 255.0));
}
// @loppu srgb

// @alku vertailu
// Kuvien ero: keskineliövirheen neliöjuuri luminanssista.
inline double rmse(const Kehys& a, const Kehys& b) {
    double s = 0;
    for (std::size_t i = 0; i < a.pikselit().size(); ++i) {
        double e = luminanssi(a.pikselit()[i]) - luminanssi(b.pikselit()[i]);
        s += e * e;
    }
    return std::sqrt(s / static_cast<double>(a.pikselit().size()));
}
inline double keskiarvo(const Kehys& a) {
    double s = 0;
    for (Vari v : a.pikselit()) s += luminanssi(v);
    return s / static_cast<double>(a.pikselit().size());
}
// @loppu vertailu

// @alku tallennus
// Valotus kerrotaan ennen koodausta; sävykuvaus luvussa Näytteistys.
inline std::vector<std::uint8_t> tavut(const Kehys& k, double valotus) {
    std::vector<std::uint8_t> t;
    for (Vari v : k.pikselit()) {
        t.push_back(srgb_tavu(valotus * v.r));
        t.push_back(srgb_tavu(valotus * v.g));
        t.push_back(srgb_tavu(valotus * v.b));
    }
    return t;
}
// FNV-1a-tiiviste sRGB-tavuista: yksikin muuttunut pikseli näkyy.
inline std::uint32_t tarkistussumma(const std::vector<std::uint8_t>& t) {
    std::uint32_t h = 2166136261u;
    for (std::uint8_t x : t) {
        h ^= x;
        h *= 16777619u;
    }
    return h;
}
inline void tallenna_ppm(const Kehys& k, const std::string& nimi,
                         double valotus = 1) {
    std::ofstream f(nimi, std::ios::binary);
    f << "P6\n" << k.leveys() << ' ' << k.korkeus() << "\n255\n";
    for (std::uint8_t x : tavut(k, valotus)) f.put(static_cast<char>(x));
}
// @loppu tallennus

// @alku ascii
// Pienennetty esikatselu tekstinä: merkki on lohkon keskikirkkaus.
inline void ascii(const Kehys& k, int lx, int ly, double valotus = 1) {
    const char* asteikko = " .:-=+*#%@";
    for (int y0 = 0; y0 + ly <= k.korkeus(); y0 += ly) {
        std::string rivi;
        for (int x0 = 0; x0 + lx <= k.leveys(); x0 += lx) {
            double s = 0;
            for (int y = y0; y < y0 + ly; ++y)
                for (int x = x0; x < x0 + lx; ++x)
                    s += srgb_tavu(valotus * luminanssi(k(x, y)));
            int ka = static_cast<int>(s / (lx * ly));
            rivi += asteikko[ka * 10 / 256];
        }
        while (!rivi.empty() && rivi.back() == ' ') rivi.pop_back();
        std::printf("|%s\n", rivi.c_str());
    }
}
// @loppu ascii

// @alku raportti
// Teksti tasattuna vasemmalle: UTF-8:n jatkotavut eivät ole merkkejä.
inline void otsake(const char* teksti, int leveys) {
    int merkit = 0;
    for (const char* c = teksti; *c; ++c) merkit += (*c & 0xC0) != 0x80;
    std::printf("%s%*s", teksti, std::max(0, leveys - merkit), "");
}
// Yhden rivin tiivistelmä: tarkistussumma ja keskimääräinen luminanssi.
inline void raportti(const char* nimi, const Kehys& k, double valotus = 1) {
    otsake(nimi, 16);
    std::printf(" summa %08x  keskiarvo %.4f\n",
                tarkistussumma(tavut(k, valotus)), keskiarvo(k));
}
// @loppu raportti
