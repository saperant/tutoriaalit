// Säteenheitto: säde vastaan pallo, laatikko ja kolmio.
#pragma once
#include "tormays.hpp"

#include <limits>

// @alku sade
struct Sade {
    Vec3 alku, suunta;  // suunta on yksikkövektori
};
struct Osuma {
    bool osuu = false;
    double t = 0;  // etäisyys säteen alusta
    Vec3 normaali;  // pinnan normaali osumakohdassa, sädettä vastaan
};
inline Vec3 kohta(const Sade& s, double t) { return s.alku + t * s.suunta; }
// @loppu sade

// @alku sade-pallo
// |alku + t suunta - keskus|^2 = r^2 on toisen asteen yhtälö t:lle.
inline Osuma sade_pallo(const Sade& s, const Pallo& p) {
    Vec3 m = s.alku - p.keskus;
    double b = piste(m, s.suunta), c = piste(m, m) - p.sade * p.sade;
    double disk = b * b - c;
    if (disk < 0) return {};
    double t = -b - std::sqrt(disk);  // lähempi juuri
    if (t < 0) return {};  // pallo on takana tai alku pallon sisällä
    return {true, t, normalisoi(kohta(s, t) - p.keskus)};
}
// @loppu sade-pallo

// @alku sade-laatikko
// Laattamenetelmä: säde on laatikossa sillä t-välillä, jolla se on
// kaikkien kolmen akselin laattojen sisällä yhtä aikaa.
inline Osuma sade_laatikko(const Sade& s, const Laatikko& l) {
    double alku[3] = {s.alku.x, s.alku.y, s.alku.z};
    double suunta[3] = {s.suunta.x, s.suunta.y, s.suunta.z};
    double lo[3] = {l.min.x, l.min.y, l.min.z};
    double hi[3] = {l.max.x, l.max.y, l.max.z};
    double tulo = 0, lahto = std::numeric_limits<double>::infinity();
    int akseli = -1;
    for (int i = 0; i < 3; ++i) {
        if (std::abs(suunta[i]) < 1e-12) {  // laatan suuntainen säde
            if (alku[i] < lo[i] || alku[i] > hi[i]) return {};
            continue;
        }
        double t1 = (lo[i] - alku[i]) / suunta[i];
        double t2 = (hi[i] - alku[i]) / suunta[i];
        if (t1 > t2) std::swap(t1, t2);
        if (t1 > tulo) {
            tulo = t1;
            akseli = i;
        }
        lahto = std::min(lahto, t2);
        if (tulo > lahto) return {};
    }
    Vec3 n;
    if (akseli == 0) n.x = suunta[0] > 0 ? -1 : 1;
    if (akseli == 1) n.y = suunta[1] > 0 ? -1 : 1;
    if (akseli == 2) n.z = suunta[2] > 0 ? -1 : 1;
    return {true, tulo, n};  // akseli -1: alku on laatikon sisällä, t = 0
}
// @loppu sade-laatikko

// @alku sade-kolmio
// Möllerin ja Trumboren menetelmä: ratkaistaan osumakohdan
// barysentriset koordinaatit u ja v sekä etäisyys t yhtä aikaa.
inline Osuma sade_kolmio(const Sade& s, const Kolmio& k) {
    Vec3 e1 = k.b - k.a, e2 = k.c - k.a;
    Vec3 p = risti(s.suunta, e2);
    double det = piste(e1, p);
    if (std::abs(det) < 1e-12) return {};  // säde on kolmion tasossa
    Vec3 m = s.alku - k.a;
    double u = piste(m, p) / det;
    if (u < 0 || u > 1) return {};
    Vec3 q = risti(m, e1);
    double v = piste(s.suunta, q) / det;
    if (v < 0 || u + v > 1) return {};
    double t = piste(e2, q) / det;
    if (t < 0) return {};
    Vec3 n = normalisoi(risti(e1, e2));
    return {true, t, piste(n, s.suunta) < 0 ? n : -n};
}
// @loppu sade-kolmio
