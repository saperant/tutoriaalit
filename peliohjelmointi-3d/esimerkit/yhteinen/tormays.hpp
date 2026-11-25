// Törmäysmuodot kolmessa ulottuvuudessa ja niiden väliset testit.
// Pallo on piste ja säde, kapseli jana ja säde: testit palautuvat
// lähimmän pisteen etsimiseen.
#pragma once
#include "vektori.hpp"

#include <algorithm>
#include <utility>

// @alku muodot
struct Pallo {
    Vec3 keskus;
    double sade = 0.5;
};
struct Laatikko {  // akselien suuntainen (AABB)
    Vec3 min, max;
};
struct Kapseli {  // jana a-b ja säde: sylinteri, jolla on pallopäät
    Vec3 a, b;
    double sade = 0.5;
};
struct Kolmio {
    Vec3 a, b, c;
};
// Testin tulos. Kun ensimmäistä muotoa siirretään matkan syvyys
// normaalin suuntaan, muodot juuri irtoavat toisistaan.
struct Kosketus {
    bool osuu = false;
    Vec3 normaali;
    double syvyys = 0;
    Vec3 piste;  // kosketuskohta toisen muodon pinnalla
};
// @loppu muodot

// @alku lahin
inline Vec3 lahin_janalla(Vec3 p, Vec3 a, Vec3 b) {
    Vec3 ab = b - a;
    double t = piste(p - a, ab) / piste(ab, ab);
    return a + std::clamp(t, 0.0, 1.0) * ab;
}
inline Vec3 lahin_laatikossa(Vec3 p, const Laatikko& l) {
    return {std::clamp(p.x, l.min.x, l.max.x),
            std::clamp(p.y, l.min.y, l.max.y),
            std::clamp(p.z, l.min.z, l.max.z)};
}
// @loppu lahin

// @alku lahin-kolmio
// Piste projisoidaan kolmion tasolle. Jos projektio on kolmion sisällä,
// se on lähin piste; muuten lähin piste on jollakin reunalla.
inline Vec3 lahin_kolmiossa(Vec3 p, const Kolmio& k) {
    Vec3 n = risti(k.b - k.a, k.c - k.a);
    Vec3 x = p - (piste(p - k.a, n) / piste(n, n)) * n;
    if (piste(risti(k.b - k.a, x - k.a), n) >= 0 &&
        piste(risti(k.c - k.b, x - k.b), n) >= 0 &&
        piste(risti(k.a - k.c, x - k.c), n) >= 0)
        return x;
    Vec3 ehdokkaat[3] = {lahin_janalla(p, k.a, k.b),
                         lahin_janalla(p, k.b, k.c),
                         lahin_janalla(p, k.c, k.a)};
    Vec3 paras = ehdokkaat[0];
    for (Vec3 e : ehdokkaat)
        if (pituus(e - p) < pituus(paras - p)) paras = e;
    return paras;
}
// @loppu lahin-kolmio

// @alku lahin-janat
// Kahden janan lähimmät pisteet. Suorien lähimmät pisteet ratkaistaan
// ensin, ja parametrit rajataan janoille yksi kerrallaan.
inline std::pair<Vec3, Vec3> lahimmat_janoilla(Vec3 a1, Vec3 b1, Vec3 a2,
                                               Vec3 b2) {
    Vec3 d1 = b1 - a1, d2 = b2 - a2, r = a1 - a2;
    double a = piste(d1, d1), e = piste(d2, d2), f = piste(d2, r);
    double b = piste(d1, d2), c = piste(d1, r);
    // Nimittäjä on nolla, kun janat ovat samansuuntaiset.
    double nimittaja = a * e - b * b;
    double s = nimittaja > 1e-12
                   ? std::clamp((b * f - c * e) / nimittaja, 0.0, 1.0)
                   : 0.0;
    double t = std::clamp((b * s + f) / e, 0.0, 1.0);
    s = std::clamp((b * t - c) / a, 0.0, 1.0);
    return {a1 + s * d1, a2 + t * d2};
}
// @loppu lahin-janat

// @alku lahin-jana-kolmio
// Janan ja kolmion lähimmät pisteet (ensin janalla, sitten kolmiossa).
inline std::pair<Vec3, Vec3> lahimmat_jana_kolmio(Vec3 p, Vec3 q,
                                                  const Kolmio& k) {
    Vec3 n = risti(k.b - k.a, k.c - k.a);
    double dp = piste(p - k.a, n), dq = piste(q - k.a, n);
    if (dp * dq < 0) {  // päät eri puolilla tasoa: lävistääkö jana?
        Vec3 x = p + (dp / (dp - dq)) * (q - p);
        if (pituus(lahin_kolmiossa(x, k) - x) < 1e-9) return {x, x};
    }
    std::pair<Vec3, Vec3> paras{p, lahin_kolmiossa(p, k)};
    auto kokeile = [&paras](Vec3 janalla, Vec3 kolmiossa) {
        if (pituus(janalla - kolmiossa) <
            pituus(paras.first - paras.second))
            paras = {janalla, kolmiossa};
    };
    kokeile(q, lahin_kolmiossa(q, k));
    Vec3 karjet[4] = {k.a, k.b, k.c, k.a};
    for (int i = 0; i < 3; ++i) {
        auto [j, r] = lahimmat_janoilla(p, q, karjet[i], karjet[i + 1]);
        kokeile(j, r);
    }
    return paras;
}
// @loppu lahin-jana-kolmio

// @alku pallotesti
// Yhteinen ydin: pallo (keskus c, säde r) ja toisen muodon lähin piste.
// vara on suunta, jota käytetään, jos keskus on täsmälleen pisteessä.
inline Kosketus pallo_ja_piste(Vec3 c, double r, Vec3 lahin,
                               Vec3 vara = {0, 1, 0}) {
    Vec3 d = c - lahin;
    double etaisyys = pituus(d);
    if (etaisyys >= r) return {};
    Vec3 n = etaisyys > 1e-9 ? (1.0 / etaisyys) * d : vara;
    return {true, n, r - etaisyys, lahin};
}
// Kaksi palloa: toinen kutistetaan pisteeksi ja toista kasvatetaan.
inline Kosketus tormaa(const Pallo& a, const Pallo& b) {
    Kosketus k = pallo_ja_piste(a.keskus, a.sade + b.sade, b.keskus);
    if (k.osuu) k.piste = b.keskus + b.sade * k.normaali;
    return k;
}
inline Kosketus tormaa(const Pallo& p, const Kolmio& k) {
    Vec3 n = normalisoi(risti(k.b - k.a, k.c - k.a));
    return pallo_ja_piste(p.keskus, p.sade, lahin_kolmiossa(p.keskus, k),
                          n);
}
inline Kosketus tormaa(const Kapseli& k, const Pallo& p) {
    Vec3 janalla = lahin_janalla(p.keskus, k.a, k.b);
    return tormaa(Pallo{janalla, k.sade}, p);
}
inline Kosketus tormaa(const Kapseli& a, const Kapseli& b) {
    auto [pa, pb] = lahimmat_janoilla(a.a, a.b, b.a, b.b);
    return tormaa(Pallo{pa, a.sade}, Pallo{pb, b.sade});
}
inline Kosketus tormaa(const Kapseli& kapseli, const Kolmio& k) {
    auto [janalla, kolmiossa] = lahimmat_jana_kolmio(kapseli.a, kapseli.b,
                                                     k);
    Vec3 n = normalisoi(risti(k.b - k.a, k.c - k.a));
    return pallo_ja_piste(janalla, kapseli.sade, kolmiossa, n);
}
// @loppu pallotesti

// @alku laatikkotesti
inline bool leikkaavat(const Laatikko& a, const Laatikko& b) {
    return a.min.x <= b.max.x && b.min.x <= a.max.x &&
           a.min.y <= b.max.y && b.min.y <= a.max.y &&
           a.min.z <= b.max.z && b.min.z <= a.max.z;
}
// Pallo ja laatikko. Jos keskus on laatikon sisällä, lähin piste on
// keskus itse, ja ulos työnnetään lähimmän sivun kautta.
inline Kosketus tormaa(const Pallo& p, const Laatikko& l) {
    Vec3 c = p.keskus, lahin = lahin_laatikossa(c, l);
    if (pituus(c - lahin) > 1e-9)
        return pallo_ja_piste(c, p.sade, lahin);
    double matkat[6] = {c.x - l.min.x, l.max.x - c.x, c.y - l.min.y,
                        l.max.y - c.y, c.z - l.min.z, l.max.z - c.z};
    Vec3 suunnat[6] = {{-1, 0, 0}, {1, 0, 0},  {0, -1, 0},
                       {0, 1, 0},  {0, 0, -1}, {0, 0, 1}};
    int i = static_cast<int>(std::min_element(matkat, matkat + 6) - matkat);
    return {true, suunnat[i], matkat[i] + p.sade,
            c + matkat[i] * suunnat[i]};
}
// @loppu laatikkotesti

// @alku ymparys
inline Laatikko ymparys(const Kolmio& k) {
    return {{std::min({k.a.x, k.b.x, k.c.x}), std::min({k.a.y, k.b.y, k.c.y}),
             std::min({k.a.z, k.b.z, k.c.z})},
            {std::max({k.a.x, k.b.x, k.c.x}), std::max({k.a.y, k.b.y, k.c.y}),
             std::max({k.a.z, k.b.z, k.c.z})}};
}
inline Laatikko ymparys(const Pallo& p) {
    Vec3 r{p.sade, p.sade, p.sade};
    return {p.keskus - r, p.keskus + r};
}
inline Laatikko ymparys(const Kapseli& k) {
    Vec3 r{k.sade, k.sade, k.sade};
    return {Vec3{std::min(k.a.x, k.b.x), std::min(k.a.y, k.b.y),
                 std::min(k.a.z, k.b.z)} - r,
            Vec3{std::max(k.a.x, k.b.x), std::max(k.a.y, k.b.y),
                 std::max(k.a.z, k.b.z)} + r};
}
inline Laatikko yhdiste(const Laatikko& a, const Laatikko& b) {
    return {{std::min(a.min.x, b.min.x), std::min(a.min.y, b.min.y),
             std::min(a.min.z, b.min.z)},
            {std::max(a.max.x, b.max.x), std::max(a.max.y, b.max.y),
             std::max(a.max.z, b.max.z)}};
}
// @loppu ymparys
