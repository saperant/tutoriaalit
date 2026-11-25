// 3x3-matriisi: kierto ja hitaustensori. Sopimukset kuten tiedostossa
// vektori.hpp: sarakevektorit ja m[rivi][sarake].
#pragma once
#include "vektori.hpp"

// @alku mat3
struct Mat3 {
    double m[3][3] = {};
};
inline Mat3 lavistaja(Vec3 d) {
    Mat3 a;
    a.m[0][0] = d.x;
    a.m[1][1] = d.y;
    a.m[2][2] = d.z;
    return a;
}
inline Mat3 operator*(const Mat3& a, const Mat3& b) {
    Mat3 c;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            for (int k = 0; k < 3; ++k) c.m[i][j] += a.m[i][k] * b.m[k][j];
    return c;
}
inline Vec3 operator*(const Mat3& a, Vec3 v) {
    return {a.m[0][0] * v.x + a.m[0][1] * v.y + a.m[0][2] * v.z,
            a.m[1][0] * v.x + a.m[1][1] * v.y + a.m[1][2] * v.z,
            a.m[2][0] * v.x + a.m[2][1] * v.y + a.m[2][2] * v.z};
}
inline Mat3 transpoosi(const Mat3& a) {
    Mat3 t;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j) t.m[i][j] = a.m[j][i];
    return t;
}
inline Vec3 sarake(const Mat3& a, int j) {
    return {a.m[0][j], a.m[1][j], a.m[2][j]};
}
// @loppu mat3

// @alku mat3-lisaa
inline Mat3 operator+(const Mat3& a, const Mat3& b) {
    Mat3 c;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j) c.m[i][j] = a.m[i][j] + b.m[i][j];
    return c;
}
// Ristitulo matriisina: ristimatriisi(r) * v == risti(r, v).
inline Mat3 ristimatriisi(Vec3 r) {
    Mat3 a;
    a.m[0][1] = -r.z;
    a.m[0][2] = r.y;
    a.m[1][0] = r.z;
    a.m[1][2] = -r.x;
    a.m[2][0] = -r.y;
    a.m[2][1] = r.x;
    return a;
}
// Käänteismatriisi kofaktoreilla. Kutsuja vastaa siitä, että matriisi
// on kääntyvä (rajoitteiden massamatriisit ovat).
inline Mat3 kaanteinen(const Mat3& a) {
    auto m = [&a](int i, int j) { return a.m[i % 3][j % 3]; };
    double c[3][3], det = 0;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            c[i][j] = m(i + 1, j + 1) * m(i + 2, j + 2) -
                      m(i + 1, j + 2) * m(i + 2, j + 1);
    for (int j = 0; j < 3; ++j) det += a.m[0][j] * c[0][j];
    Mat3 k;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j) k.m[i][j] = c[j][i] / det;
    return k;
}
// @loppu mat3-lisaa
