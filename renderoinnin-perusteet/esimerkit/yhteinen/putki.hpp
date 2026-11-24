// Ohjelmistona toteutettu grafiikkaputki. Verteksi- ja
// fragmenttivarjostimet ovat funktioita, kuten näytönohjaimessa.
#pragma once
#include <array>
#include <cmath>
#include <cstddef>
#include <type_traits>
#include <vector>

#include "kuva.hpp"
#include "malli.hpp"
#include "rasteri.hpp"
#include "vektori.hpp"

// @alku tulos
// Verteksivarjostimen tulos: paikka leikkausavaruudessa ja N
// vaihtelevaa arvoa (varying), jotka interpoloidaan kolmion yli.
template <std::size_t N>
struct Tulos {
    Vec4 paikka;
    std::array<double, N> v{};
};

template <std::size_t N>
Tulos<N> sekoita(const Tulos<N>& a, const Tulos<N>& b, double s) {
    Tulos<N> t;
    t.paikka = {a.paikka.x + s * (b.paikka.x - a.paikka.x),
                a.paikka.y + s * (b.paikka.y - a.paikka.y),
                a.paikka.z + s * (b.paikka.z - a.paikka.z),
                a.paikka.w + s * (b.paikka.w - a.paikka.w)};
    for (std::size_t i = 0; i < N; ++i)
        t.v[i] = a.v[i] + s * (b.v[i] - a.v[i]);
    return t;
}
// @loppu tulos

// @alku kohde
struct Asetukset {
    bool perspektiivikorjaus = true;
    bool leikkaa = true;      // lähitason leikkaus
    bool syvyystesti = true;
    bool karsinta = true;     // takapintojen karsinta
    int syvyysbitit = 0;      // 0 = liukuluku, muuten kokonaisluku
    bool derivaatat = false;  // vaihtelevien muutos naapuripikseliin
};

struct Tilasto {
    long kolmiot = 0, hylatyt = 0, leikatut = 0, karsitut = 0;
    long fragmentit = 0, syvyys_hylatyt = 0;
};

// Piirtokohde: lineaarinen väripuskuri ja syvyyspuskuri.
struct Kohde {
    int l, k;
    std::vector<Vari> vari;
    std::vector<double> syvyys;
    Tilasto tilasto;

    Kohde(int leveys, int korkeus, Vari tausta = {})
        : l(leveys), k(korkeus),
          vari(static_cast<std::size_t>(leveys) * korkeus, tausta),
          syvyys(static_cast<std::size_t>(leveys) * korkeus, 1.0) {}

    Kuva kuvaksi() const {
        Kuva kuva(l, k);
        for (int y = 0; y < k; ++y)
            for (int x = 0; x < l; ++x)
                kuva(x, y) =
                    koodaa(vari[static_cast<std::size_t>(y * l + x)]);
        return kuva;
    }
    // Ylinäytteistys: n x n pikselin lohkon keskiarvo valona.
    Kuva pienennetty(int n) const {
        Kuva kuva(l / n, k / n);
        for (int y = 0; y < k / n; ++y)
            for (int x = 0; x < l / n; ++x) {
                Vari s;
                for (int j = 0; j < n; ++j)
                    for (int i = 0; i < n; ++i)
                        s = s + vari[static_cast<std::size_t>(
                                (y * n + j) * l + x * n + i)];
                kuva(x, y) = koodaa((1.0 / (n * n)) * s);
            }
        return kuva;
    }
};
// @loppu kohde

// @alku fragmentti
template <class V>
struct Fragmentti {
    int x, y;
    double syvyys;
    V ddx{}, ddy{};  // vaihtelevien muutos pikselin askeleella
};
// @loppu fragmentti

// @alku leikkaus
// Sutherland-Hodgman yhtä tasoa vastaan: lähitaso z = -w on
// leikkausavaruudessa ehto z + w >= 0. Kolmiosta tulee 0, 3 tai 4
// kärkeä. Interpolointi on oikein, koska leikkausavaruus on vielä
// lineaarinen (perspektiivijakoa ei ole tehty).
template <class T>
std::vector<T> leikkaa_lahitaso(const std::vector<T>& sisaan) {
    std::vector<T> ulos;
    auto etaisyys = [](const T& t) { return t.paikka.z + t.paikka.w; };
    for (std::size_t i = 0; i < sisaan.size(); ++i) {
        const T& a = sisaan[i];
        const T& b = sisaan[(i + 1) % sisaan.size()];
        double da = etaisyys(a), db = etaisyys(b);
        if (da >= 0) ulos.push_back(a);
        if ((da >= 0) != (db >= 0))
            ulos.push_back(sekoita(a, b, da / (da - db)));
    }
    return ulos;
}
// @loppu leikkaus

// @alku hylkaa
// Koko kolmio saman leikkaustason ulkopuolella: ei mitään piirrettävää.
template <class T>
bool kokonaan_ulkona(const T& a, const T& b, const T& c) {
    auto ulkona = [&](auto ehto) { return ehto(a) && ehto(b) && ehto(c); };
    return ulkona([](const T& t) { return t.paikka.x > t.paikka.w; }) ||
           ulkona([](const T& t) { return t.paikka.x < -t.paikka.w; }) ||
           ulkona([](const T& t) { return t.paikka.y > t.paikka.w; }) ||
           ulkona([](const T& t) { return t.paikka.y < -t.paikka.w; }) ||
           ulkona([](const T& t) { return t.paikka.z > t.paikka.w; }) ||
           ulkona([](const T& t) { return t.paikka.z < -t.paikka.w; });
}
// @loppu hylkaa

// @alku ruutu
// Perspektiivijako ja näkymäportti: NDC [-1, 1] -> pikselit, y alas.
struct Ruutupiste {
    Vec2 p;
    double z;     // syvyys 0..1
    double kw;    // 1 / w perspektiivikorjausta varten
};
inline Ruutupiste ruudulle(Vec4 c, int l, int k) {
    double kw = 1.0 / c.w;
    double x = c.x * kw, y = c.y * kw, z = c.z * kw;
    return {{(x + 1) * 0.5 * l, (1 - y) * 0.5 * k}, (z + 1) * 0.5, kw};
}
// @loppu ruutu

// @alku interpolointi
// Painot ruudulla ovat lineaarisia ruudulla, mutta vaihtelevat arvot
// ovat lineaarisia maailmassa. Korjaus: interpoloi v / w ja 1 / w
// ja jaa ne keskenään.
inline Bary korjaa(Bary b, const Ruutupiste* r) {
    double a0 = b.l0 * r[0].kw, a1 = b.l1 * r[1].kw, a2 = b.l2 * r[2].kw;
    double s = a0 + a1 + a2;
    return {a0 / s, a1 / s, a2 / s};
}
template <std::size_t N>
std::array<double, N> interpoloi(const Tulos<N>* t, Bary b) {
    std::array<double, N> v{};
    for (std::size_t i = 0; i < N; ++i)
        v[i] = b.l0 * t[0].v[i] + b.l1 * t[1].v[i] + b.l2 * t[2].v[i];
    return v;
}
// @loppu interpolointi

// @alku kolmio
template <std::size_t N, class FV>
void piirra_kolmio(Kohde& kohde, const Tulos<N>* t, FV& fv,
                   const Asetukset& as) {
    Ruutupiste r[3];
    for (int i = 0; i < 3; ++i)
        r[i] = ruudulle(t[i].paikka, kohde.l, kohde.k);
    // Kiertosuunta ruudulla (sama kaava kuin reunafunktiossa):
    // etupinta on vastapäiväinen ja sen ala positiivinen.
    double ala = (r[2].p.x - r[0].p.x) * (r[1].p.y - r[0].p.y) -
                 (r[2].p.y - r[0].p.y) * (r[1].p.x - r[0].p.x);
    if (as.karsinta && ala <= 0) {
        ++kohde.tilasto.karsitut;
        return;
    }
    double porras = as.syvyysbitit
                        ? std::ldexp(1.0, as.syvyysbitit) - 1 : 0;
    using V = std::array<double, N>;
    auto arvot = [&](Bary b) {
        return interpoloi(t, as.perspektiivikorjaus ? korjaa(b, r) : b);
    };
    rasteroi(r[0].p, r[1].p, r[2].p, kohde.l, kohde.k,
             [&](int x, int y, Bary b) {
        double z = b.l0 * r[0].z + b.l1 * r[1].z + b.l2 * r[2].z;
        if (porras > 0) z = std::floor(z * porras + 0.5) / porras;
        std::size_t i = static_cast<std::size_t>(y) * kohde.l + x;
        if (as.syvyystesti && !(z < kohde.syvyys[i])) {
            ++kohde.tilasto.syvyys_hylatyt;  // hylätään ennen varjostusta
            return;
        }
        Fragmentti<V> f{x, y, z};
        V v = arvot(b);
        if (as.derivaatat) {
            Vec2 kp = {x + 0.5, y + 0.5};
            auto naapuri = [&](double dx, double dy) {
                return arvot(barysentriset(r[0].p, r[1].p, r[2].p,
                                           {kp.x + dx, kp.y + dy}));
            };
            V vx = naapuri(1, 0), vy = naapuri(0, 1);
            for (std::size_t j = 0; j < N; ++j) {
                f.ddx[j] = vx[j] - v[j];
                f.ddy[j] = vy[j] - v[j];
            }
        }
        ++kohde.tilasto.fragmentit;
        kohde.vari[i] = fv(v, f);
        if (as.syvyystesti) kohde.syvyys[i] = z;
    });
}
// @loppu kolmio

// @alku piirra
// Koko putki yhdelle mallille: verteksivaihe, kokoaminen kolmioiksi,
// hylkäys ja leikkaus, rasterointi ja fragmenttivaihe.
template <class VV, class FV>
void piirra(Kohde& kohde, const Malli& malli, VV&& vv, FV&& fv,
            const Asetukset& as = {}) {
    using T = std::invoke_result_t<VV&, const Verteksi&>;
    std::vector<T> tulokset;
    for (const Verteksi& v : malli.verteksit) tulokset.push_back(vv(v));
    for (const auto& kolmio : malli.kolmiot) {
        ++kohde.tilasto.kolmiot;
        std::vector<T> moni = {tulokset[kolmio[0]], tulokset[kolmio[1]],
                               tulokset[kolmio[2]]};
        if (kokonaan_ulkona(moni[0], moni[1], moni[2])) {
            ++kohde.tilasto.hylatyt;
            continue;
        }
        bool osittain = false;
        for (const T& t : moni) osittain |= t.paikka.z + t.paikka.w < 0;
        if (as.leikkaa && osittain) {
            ++kohde.tilasto.leikatut;
            moni = leikkaa_lahitaso(moni);
        }
        // Monikulmio viuhkaksi: (0, 1, 2), (0, 2, 3), ...
        for (std::size_t i = 1; i + 1 < moni.size(); ++i) {
            T k3[3] = {moni[0], moni[i], moni[i + 1]};
            piirra_kolmio(kohde, k3, fv, as);
        }
    }
}
// @loppu piirra
