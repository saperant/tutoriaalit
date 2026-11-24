// Vektorit ja 4x4-matriisit (sarakevektorit, kuten lineaarialgebrassa).
#pragma once
#include <cmath>

// @alku vektorit
struct Vec2 {
    double x = 0, y = 0;
};
struct Vec3 {
    double x = 0, y = 0, z = 0;
};
struct Vec4 {
    double x = 0, y = 0, z = 0, w = 0;
};

inline Vec3 operator+(Vec3 a, Vec3 b) {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}
inline Vec3 operator-(Vec3 a, Vec3 b) {
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}
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
inline Vec3 normalisoi(Vec3 a) {
    return (1.0 / std::sqrt(piste(a, a))) * a;
}
// @loppu vektorit

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
inline Vec4 piste4(Vec3 p) { return {p.x, p.y, p.z, 1}; }   // w = 1
inline Vec4 suunta4(Vec3 d) { return {d.x, d.y, d.z, 0}; }  // w = 0
inline Vec3 xyz(Vec4 v) { return {v.x, v.y, v.z}; }
// @loppu matriisi

// @alku muunnokset
inline Mat4 siirto(double x, double y, double z) {
    Mat4 a = yksikko();
    a.m[0][3] = x;
    a.m[1][3] = y;
    a.m[2][3] = z;
    return a;
}
inline Mat4 skaalaus(double x, double y, double z) {
    Mat4 a = yksikko();
    a.m[0][0] = x;
    a.m[1][1] = y;
    a.m[2][2] = z;
    return a;
}
// Kierrot annetaan kosinina ja sinina, jotta tulos ei riipu
// trigonometristen funktioiden toteutuksesta.
inline Mat4 kierto_y(double c, double s) {
    Mat4 a = yksikko();
    a.m[0][0] = c;
    a.m[0][2] = s;
    a.m[2][0] = -s;
    a.m[2][2] = c;
    return a;
}
inline Mat4 kierto_x(double c, double s) {
    Mat4 a = yksikko();
    a.m[1][1] = c;
    a.m[1][2] = -s;
    a.m[2][1] = s;
    a.m[2][2] = c;
    return a;
}
// @loppu muunnokset

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
// Leikkausavaruudesta NDC-kuutioon [-1, 1]^3 jakamalla w:llä.
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

// @alku normaalit
// Normaalimatriisi: mallimatriisin 3x3-osan kofaktorimatriisi, joka
// on käänteismatriisin transpoosi kerrottuna determinantilla.
// Normalisointi poistaa kertoimen, joten jakoa ei tarvita.
inline Vec3 muunna_normaali(const Mat4& a, Vec3 n) {
    auto m = [&a](int i, int j) { return a.m[i % 3][j % 3]; };
    double c[3][3];
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            c[i][j] = m(i + 1, j + 1) * m(i + 2, j + 2) -
                      m(i + 1, j + 2) * m(i + 2, j + 1);
    return normalisoi({c[0][0] * n.x + c[0][1] * n.y + c[0][2] * n.z,
                       c[1][0] * n.x + c[1][1] * n.y + c[1][2] * n.z,
                       c[2][0] * n.x + c[2][1] * n.y + c[2][2] * n.z});
}
// @loppu normaalit
