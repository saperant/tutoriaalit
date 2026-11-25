// Näkymäpuu: jokaisella solmulla on paikallinen muunnos vanhempaansa
// nähden. Maailmamuunnos lasketaan kertomalla matriisit juuresta alas,
// ja lopuksi kamera ja perspektiiviprojektio vievät pisteen ruudulle.
#include <array>
#include <cmath>
#include <numbers>
#include <print>
#include <string>
#include <vector>

// @alku matriisi
struct V3 {
    double x, y, z;
};

struct M4 {  // 4x4-matriisi, sarakevektorit: p' = M p
    std::array<double, 16> a{};
    static M4 yksikko() {
        M4 m;
        m.a[0] = m.a[5] = m.a[10] = m.a[15] = 1.0;
        return m;
    }
    double& operator()(int r, int c) { return a[r * 4 + c]; }
    double operator()(int r, int c) const { return a[r * 4 + c]; }
};

M4 operator*(const M4& p, const M4& q) {
    M4 t;
    for (int r = 0; r < 4; ++r) {
        for (int c = 0; c < 4; ++c) {
            for (int k = 0; k < 4; ++k) {
                t(r, c) += p(r, k) * q(k, c);
            }
        }
    }
    return t;
}

V3 muunna(const M4& m, V3 v) {
    const double w = m(3, 0) * v.x + m(3, 1) * v.y + m(3, 2) * v.z + m(3, 3);
    return {(m(0, 0) * v.x + m(0, 1) * v.y + m(0, 2) * v.z + m(0, 3)) / w,
            (m(1, 0) * v.x + m(1, 1) * v.y + m(1, 2) * v.z + m(1, 3)) / w,
            (m(2, 0) * v.x + m(2, 1) * v.y + m(2, 2) * v.z + m(2, 3)) / w};
}

M4 siirto(double x, double y, double z) {
    M4 m = M4::yksikko();
    m(0, 3) = x;
    m(1, 3) = y;
    m(2, 3) = z;
    return m;
}

M4 kierto_y(double kulma) {  // kierto pystyakselin ympäri
    M4 m = M4::yksikko();
    m(0, 0) = m(2, 2) = std::cos(kulma);
    m(0, 2) = std::sin(kulma);
    m(2, 0) = -std::sin(kulma);
    return m;
}
// @loppu matriisi

// @alku puu
struct Solmu {
    std::string nimi;
    M4 paikallinen = M4::yksikko();
    int vanhempi = -1;     // -1 = juuri
    M4 maailma = M4::yksikko();
};

// Vanhemmat ovat taulukossa ennen lapsiaan, joten yksi läpikäynti
// riittää eikä rekursiota tarvita.
void paivita_maailma(std::vector<Solmu>& puu) {
    for (Solmu& s : puu) {
        s.maailma = s.vanhempi < 0
                        ? s.paikallinen
                        : puu[static_cast<std::size_t>(s.vanhempi)].maailma *
                              s.paikallinen;
    }
}
// @loppu puu

// @alku projektio
// Perspektiivi: kamera katsoo -z-suuntaan, näkökenttä 90 astetta.
// Ruudun koordinaatit pikseleinä (0, 0) vasemmassa yläkulmassa.
std::pair<int, int> ruudulle(const M4& nakyma, V3 p, int leveys,
                             int korkeus) {
    const V3 k = muunna(nakyma, p);          // kameran koordinaatistoon
    const double nx = k.x / -k.z;            // jako syvyydellä
    const double ny = k.y / -k.z;
    return {static_cast<int>(std::lround((nx + 1.0) * 0.5 * leveys)),
            static_cast<int>(std::lround((1.0 - ny) * 0.5 * korkeus))};
}
// @loppu projektio

int main() {
    std::vector<Solmu> puu = {
        {"lautta", siirto(0, 0, -10), -1},
        {"auto", siirto(2, 0.5, 0), 0},
        {"pyörä", siirto(0.8, -0.3, 0.6), 1},
    };
    const M4 nakyma = siirto(0, -2, 0);  // kamera 2 m ylempänä
    for (double kulma : {0.0, 90.0}) {
        puu[0].paikallinen = siirto(0, 0, -10) *
                             kierto_y(kulma * std::numbers::pi / 180.0);
        paivita_maailma(puu);
        std::println("lautta kääntynyt {:.0f} astetta:", kulma);
        for (const Solmu& s : puu) {
            const V3 p = muunna(s.maailma, {0, 0, 0});
            auto [x, y] = ruudulle(nakyma, p, 320, 240);
            std::println("  {:6} maailmassa ({:5.2f}, {:5.2f}, {:6.2f}), "
                         "ruudulla ({}, {})",
                         s.nimi, p.x, p.y, p.z, x, y);
        }
    }
}
