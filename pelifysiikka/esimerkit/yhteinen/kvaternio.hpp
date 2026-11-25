// Yksikkökvaternio kappaleen asentona. Perusteet (akseli ja kulma,
// tulo, normalisointi) ovat taidossa 3D-peliohjelmointi; tässä ovat ne
// operaatiot, joita dynamiikka tarvitsee.
#pragma once
#include "matriisi3.hpp"

struct Kvat {
    double w = 1, x = 0, y = 0, z = 0;
};
inline Kvat akselikulma(Vec3 akseli, double kulma) {
    double s = std::sin(kulma / 2);
    return {std::cos(kulma / 2), s * akseli.x, s * akseli.y, s * akseli.z};
}
inline Kvat operator*(Kvat a, Kvat b) {
    return {a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
            a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
            a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
            a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w};
}
inline Kvat liitto(Kvat q) { return {q.w, -q.x, -q.y, -q.z}; }
inline Kvat normalisoi(Kvat q) {
    double k =
        1.0 / std::sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    return {k * q.w, k * q.x, k * q.y, k * q.z};
}
inline Vec3 kierra(Kvat q, Vec3 v) {
    Vec3 u{q.x, q.y, q.z};
    Vec3 t = 2.0 * risti(u, v);
    return v + q.w * t + risti(u, t);
}

// @alku kiertomatriisi
// Kiertomatriisi: kierretyt kanta-akselit sarakkeina.
inline Mat3 kiertomatriisi(Kvat q) {
    Mat3 r;
    Vec3 akselit[3] = {kierra(q, {1, 0, 0}), kierra(q, {0, 1, 0}),
                       kierra(q, {0, 0, 1})};
    for (int j = 0; j < 3; ++j) {
        r.m[0][j] = akselit[j].x;
        r.m[1][j] = akselit[j].y;
        r.m[2][j] = akselit[j].z;
    }
    return r;
}
// @loppu kiertomatriisi

// @alku asennon-askel
// Asennon askel kulmanopeudella w: dq/dt = 1/2 * (0, w) * q.
// Yhteenlasku vie kvaternion pois yksikköpallolta, joten tulos
// normalisoidaan joka askeleella.
inline Kvat kierra_askel(Kvat q, Vec3 w, double dt) {
    Kvat dq = Kvat{0, w.x, w.y, w.z} * q;
    return normalisoi({q.w + 0.5 * dt * dq.w, q.x + 0.5 * dt * dq.x,
                       q.y + 0.5 * dt * dq.y, q.z + 0.5 * dt * dq.z});
}
// @loppu asennon-askel

// Kuvitusta varten: kierto ja siirto 4x4-mallimatriisina.
inline Mat4 mallimatriisi(Vec3 sijainti, Kvat q) {
    Mat4 a = yksikko();
    Mat3 r = kiertomatriisi(q);
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j) a.m[i][j] = r.m[i][j];
    a.m[0][3] = sijainti.x;
    a.m[1][3] = sijainti.y;
    a.m[2][3] = sijainti.z;
    return a;
}
