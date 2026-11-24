// BVH: sama kuva raakahaulla ja kahdella jakotavalla.
#include <cstdio>
#include <vector>

#include "yhteinen/bvh.hpp"
#include "yhteinen/kamera.hpp"
#include "yhteinen/kuva.hpp"
#include "yhteinen/naytteet.hpp"
#include "yhteinen/satunnainen.hpp"

const int L = 32, K = 24;

// @alku kohtaus
// Laaja, harva maasto ja sen keskellä tiheä pallo: kolmiot ovat
// jakautuneet epätasaisesti, kuten oikeissa kohtauksissa.
std::vector<Kolmio> kohtaus() {
    std::vector<Kolmio> k;
    const int N = 32;
    auto maa = [](int i, int j) {
        Pcg32 g(static_cast<std::uint64_t>(i) * 1000 + j);
        return Vec3{-4 + 8.0 * i / N, 0.15 * g.tasainen(), -4 + 8.0 * j / N};
    };
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j) {
            k.push_back({maa(i, j), maa(i, j + 1), maa(i + 1, j + 1)});
            k.push_back({maa(i, j), maa(i + 1, j + 1), maa(i + 1, j)});
        }
    const int P = 32, Q = 16;   // pallon pituus- ja leveyspiirit
    auto pallo = [](int i, int j) {
        double phi = 2 * PII * i / P, th = PII * j / Q;
        return Vec3{0.6 * std::sin(th) * std::cos(phi),
                    0.8 + 0.6 * std::cos(th),
                    0.6 * std::sin(th) * std::sin(phi)};
    };
    for (int i = 0; i < P; ++i)
        for (int j = 0; j < Q; ++j) {
            k.push_back({pallo(i, j), pallo(i + 1, j), pallo(i + 1, j + 1)});
            k.push_back({pallo(i, j), pallo(i + 1, j + 1), pallo(i, j + 1)});
        }
    return k;
}
// @loppu kohtaus

int syvyys(const Bvh& b, int i) {
    const Solmu& s = b.solmut[i];
    if (s.maara > 0) return 1;
    return 1 + std::max(syvyys(b, s.eka), syvyys(b, s.eka + 1));
}

// @alku raaka
BvhOsuma raakahaku(const std::vector<Kolmio>& kolmiot, const Sade& s,
                   BvhLaskuri& laskuri) {
    BvhOsuma o;
    for (int i = 0; i < static_cast<int>(kolmiot.size()); ++i) {
        ++laskuri.kolmiot;
        double t = leikkaa_kolmio(kolmiot[i], s, 0, o.t).t;
        if (t < o.t) o = {t, i};
    }
    return o;
}
// @loppu raaka

// @alku vertailu
template <class Haku>
void renderoi(const char* nimi, const std::vector<Kolmio>& kolmiot,
              Haku haku) {
    Kamera k = kamera({2.5, 2.2, -3.5}, {0, 0.5, 0}, {0, 1, 0}, 1.7, L, K);
    Vec3 valo = normalisoi({-0.5, 1, -0.4});
    Kehys kuva(L, K);
    BvhLaskuri laskuri;
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            BvhOsuma o = haku(k.sade(x + 0.5, y + 0.5), laskuri);
            double v = 0.1;
            if (o.kolmio >= 0)
                v = 0.05 + 0.8 * std::fabs(piste(normaali(kolmiot[o.kolmio]),
                                                 valo));
            kuva(x, y) = {v, v, v};
        }
    raportti(nimi, kuva);
    std::printf("    säteeltä: %.1f laatikkoa, %.1f kolmiota\n",
                static_cast<double>(laskuri.laatikot) / (L * K),
                static_cast<double>(laskuri.kolmiot) / (L * K));
}
// @loppu vertailu

int main() {
    // @alku main
    std::vector<Kolmio> kolmiot = kohtaus();
    std::printf("kolmioita %zu\n", kolmiot.size());
    Bvh keski = rakenna_bvh(kolmiot, Jako::keskikohta);
    Bvh sah = rakenna_bvh(kolmiot, Jako::sah);
    for (auto [nimi, b] : {std::pair{"keskikohta", &keski},
                           std::pair{"SAH", &sah}})
        std::printf("%-10s solmuja %5zu, syvyys %d\n", nimi,
                    b->solmut.size(), syvyys(*b, 0));
    renderoi("raakahaku", kolmiot, [&](const Sade& s, BvhLaskuri& l) {
        return raakahaku(kolmiot, s, l);
    });
    renderoi("BVH keskikohta", kolmiot, [&](const Sade& s, BvhLaskuri& l) {
        return leikkaa_bvh(keski, kolmiot, s, l);
    });
    renderoi("BVH SAH", kolmiot, [&](const Sade& s, BvhLaskuri& l) {
        return leikkaa_bvh(sah, kolmiot, s, l);
    });
    // @loppu main

    // @alku satunnaiset
    // Satunnaiset säteet joka suuntaan: BVH:n on löydettävä täsmälleen
    // sama lähin osuma kuin raakahaun.
    Pcg32 g(7);
    BvhLaskuri lr, lk, ls;
    int eroja = 0;
    for (int i = 0; i < 400; ++i) {
        Vec3 o{6 * g.tasainen() - 3, 2 * g.tasainen(), 6 * g.tasainen() - 3};
        Vec3 d = normalisoi({2 * g.tasainen() - 1, 2 * g.tasainen() - 1,
                             2 * g.tasainen() - 1});
        Sade s{o, d};
        double t = raakahaku(kolmiot, s, lr).t;
        eroja += leikkaa_bvh(keski, kolmiot, s, lk).t != t;
        eroja += leikkaa_bvh(sah, kolmiot, s, ls).t != t;
    }
    std::printf("satunnaiset säteet: %d eroa raakahakuun\n", eroja);
    std::printf("    keskikohta %.1f laatikkoa, %.1f kolmiota\n",
                lk.laatikot / 400.0, lk.kolmiot / 400.0);
    std::printf("    SAH        %.1f laatikkoa, %.1f kolmiota\n",
                ls.laatikot / 400.0, ls.kolmiot / 400.0);
    // @loppu satunnaiset
}
