// Vektorit ja 4x4-matriisit (sama tiedosto kuin taidossa
// 3D-peliohjelmointi). Sopimukset kuten taidossa Renderöinnin
// perusteet: oikeakätinen koordinaatisto, y ylös, kamera katsoo
// suuntaan -z, sarakevektorit ja m[rivi][sarake]. Yksikkö on metri.
#pragma once
#include "liukuluvut.hpp"

#include <cmath>

// @alku vektori
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
inline Vec3 lerp(Vec3 a, Vec3 b, double t) { return a + t * (b - a); }
// @loppu vektori

struct Vec4 {
    double x = 0, y = 0, z = 0, w = 0;
};

// @alku matriisi
struct Mat4 {
    double m[4][4] = {};  // m[rivi][sarake]
};
inline Mat4 yksikko() {
    Mat4 a;
    for (int i = 0; i < 4; ++i) a.m[i][i] = 1;
    return a;
}
inline Mat4 operator*(const Mat4& a, const Mat4& b) {
    Mat4 c;
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            for (int k = 0; k < 4; ++k) c.m[i][j] += a.m[i][k] * b.m[k][j];
    return c;
}
inline Vec4 operator*(const Mat4& a, Vec4 v) {
    double p[4] = {v.x, v.y, v.z, v.w}, t[4] = {};
    for (int i = 0; i < 4; ++i)
        for (int k = 0; k < 4; ++k) t[i] += a.m[i][k] * p[k];
    return {t[0], t[1], t[2], t[3]};
}
// Piste (w = 1) kulkee siirron läpi, suunta (w = 0) ei.
inline Vec3 muunna_piste(const Mat4& a, Vec3 p) {
    Vec4 v = a * Vec4{p.x, p.y, p.z, 1};
    return {v.x, v.y, v.z};
}
inline Vec3 muunna_suunta(const Mat4& a, Vec3 d) {
    Vec4 v = a * Vec4{d.x, d.y, d.z, 0};
    return {v.x, v.y, v.z};
}
inline Mat4 siirto(Vec3 t) {
    Mat4 a = yksikko();
    a.m[0][3] = t.x;
    a.m[1][3] = t.y;
    a.m[2][3] = t.z;
    return a;
}
inline Mat4 skaalaus(Vec3 s) {
    Mat4 a = yksikko();
    a.m[0][0] = s.x;
    a.m[1][1] = s.y;
    a.m[2][2] = s.z;
    return a;
}
// @loppu matriisi

// @alku affiini
// Affiinin muunnoksen (kierto, skaalaus, siirto) käänteismatriisi:
// 3x3-osa käännetään kofaktoreilla ja siirto kuljetetaan sen läpi.
inline Mat4 kaanteinen(const Mat4& a) {
    auto m = [&a](int i, int j) { return a.m[i % 3][j % 3]; };
    double c[3][3], det = 0;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            c[i][j] = m(i + 1, j + 1) * m(i + 2, j + 2) -
                      m(i + 1, j + 2) * m(i + 2, j + 1);
    for (int j = 0; j < 3; ++j) det += a.m[0][j] * c[0][j];
    Mat4 k = yksikko();
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j) k.m[i][j] = c[j][i] / det;
    for (int i = 0; i < 3; ++i)
        k.m[i][3] = -(k.m[i][0] * a.m[0][3] + k.m[i][1] * a.m[1][3] +
                      k.m[i][2] * a.m[2][3]);
    return k;
}
// @loppu affiini

// @alku kamera
// Näkymämatriisi: kameran akselit riveinä ja silmä origoon.
inline Mat4 katse(Vec3 silma, Vec3 kohde, Vec3 ylos) {
    Vec3 z = normalisoi(silma - kohde);  // kamera katsoo suuntaan -z
    Vec3 x = normalisoi(risti(ylos, z));
    Vec3 y = risti(z, x);
    Mat4 a = yksikko();
    Vec3 akselit[3] = {x, y, z};
    for (int i = 0; i < 3; ++i) {
        a.m[i][0] = akselit[i].x;
        a.m[i][1] = akselit[i].y;
        a.m[i][2] = akselit[i].z;
        a.m[i][3] = -piste(akselit[i], silma);
    }
    return a;
}
// Perspektiivi: f = 1 / tan(fov/2), suhde = leveys / korkeus.
inline Mat4 perspektiivi(double f, double suhde, double lahi,
                         double kauka) {
    Mat4 a;
    a.m[0][0] = f / suhde;
    a.m[1][1] = f;
    a.m[2][2] = (kauka + lahi) / (lahi - kauka);
    a.m[2][3] = 2 * kauka * lahi / (lahi - kauka);
    a.m[3][2] = -1;  // w = -z: etäisyys kamerasta
    return a;
}
// @loppu kamera

inline constexpr double PII = 3.14159265358979323846;
inline constexpr double rad(double asteet) { return asteet * PII / 180.0; }
inline constexpr double aste(double radiaanit) {
    return radiaanit * 180.0 / PII;
}
