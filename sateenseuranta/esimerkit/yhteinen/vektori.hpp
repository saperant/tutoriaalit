// Kolmiulotteiset vektorit ja ortonormaali kanta.
#pragma once
#include <cmath>

// @alku vektorit
struct Vec3 {
    double x = 0, y = 0, z = 0;
};

inline Vec3 operator+(Vec3 a, Vec3 b) {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}
inline Vec3 operator-(Vec3 a, Vec3 b) {
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}
inline Vec3 operator-(Vec3 a) { return {-a.x, -a.y, -a.z}; }
inline Vec3 operator*(double k, Vec3 a) {
    return {k * a.x, k * a.y, k * a.z};
}
inline double piste(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}
inline Vec3 risti(Vec3 a, Vec3 b) {
    return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x};
}
inline double pituus(Vec3 a) { return std::sqrt(piste(a, a)); }
inline Vec3 normalisoi(Vec3 a) { return (1.0 / pituus(a)) * a; }
// Komponentti indeksillä 0, 1 tai 2 (akselin valinta BVH:ssa).
inline double akseli(Vec3 a, int i) {
    return i == 0 ? a.x : i == 1 ? a.y : a.z;
}
// @loppu vektorit

// @alku heijastus
// Peiliheijastus: d tulee pintaan, n on yksikkönormaali.
inline Vec3 heijasta(Vec3 d, Vec3 n) { return d - 2 * piste(d, n) * n; }
// @loppu heijastus

// @alku kanta
// Ortonormaali kanta, jonka z-akseli on yksikkövektori n
// (Duff ym. 2017). Näytteet lasketaan paikallisessa kannassa, jossa
// normaali on (0, 0, 1), ja käännetään maailmaan.
struct Kanta {
    Vec3 t, b, n;
    Vec3 maailmaan(Vec3 v) const { return v.x * t + v.y * b + v.z * n; }
    Vec3 paikalliseen(Vec3 v) const {
        return {piste(v, t), piste(v, b), piste(v, n)};
    }
};
inline Kanta kanta(Vec3 n) {
    double s = std::copysign(1.0, n.z);
    double a = -1.0 / (s + n.z);
    double b = n.x * n.y * a;
    return {{1 + s * n.x * n.x * a, s * b, -s * n.x},
            {b, s + n.y * n.y * a, -n.y}, n};
}
// @loppu kanta
