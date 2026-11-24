// Pieni matriisikirjasto renderöintiesimerkeille: 4×4-matriisit
// sarakkeittain (kuten GLSL), kamera- ja projektiomatriisit.
// Oikeissa projekteissa käytetään esim. GLM-kirjastoa.
#pragma once

#include <array>
#include <cmath>

struct Vec3 {
    float x, y, z;
};
inline Vec3 operator-(Vec3 a, Vec3 b) {
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}
inline float piste(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}
inline Vec3 risti(Vec3 a, Vec3 b) {
    return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x};
}
inline Vec3 normalisoi(Vec3 a) {
    const float p = std::sqrt(piste(a, a));
    return {a.x / p, a.y / p, a.z / p};
}

// m[sarake * 4 + rivi]
struct Mat4 {
    std::array<float, 16> m{};

    static Mat4 yksikko() {
        Mat4 r;
        r.m[0] = r.m[5] = r.m[10] = r.m[15] = 1.0f;
        return r;
    }
    float& operator()(int rivi, int sarake) {
        return m[static_cast<std::size_t>(sarake * 4 + rivi)];
    }
    float operator()(int rivi, int sarake) const {
        return m[static_cast<std::size_t>(sarake * 4 + rivi)];
    }
};

inline Mat4 operator*(const Mat4& a, const Mat4& b) {
    Mat4 r;
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            float s = 0.0f;
            for (int k = 0; k < 4; ++k) {
                s += a(i, k) * b(k, j);
            }
            r(i, j) = s;
        }
    }
    return r;
}

// Kamera pisteessä silma katsoo pistettä kohde (oikeakätinen, y ylös).
inline Mat4 katse(Vec3 silma, Vec3 kohde, Vec3 ylos) {
    const Vec3 f = normalisoi(kohde - silma);
    const Vec3 s = normalisoi(risti(f, ylos));
    const Vec3 u = risti(s, f);
    Mat4 r = Mat4::yksikko();
    r(0, 0) = s.x; r(0, 1) = s.y; r(0, 2) = s.z;
    r(1, 0) = u.x; r(1, 1) = u.y; r(1, 2) = u.z;
    r(2, 0) = -f.x; r(2, 1) = -f.y; r(2, 2) = -f.z;
    r(0, 3) = -piste(s, silma);
    r(1, 3) = -piste(u, silma);
    r(2, 3) = piste(f, silma);
    return r;
}

// Perspektiiviprojektio OpenGL:n syvyysalueelle −1…1.
inline Mat4 perspektiivi(float nakokulma, float suhde, float lahi,
                         float kauka) {
    const float t = 1.0f / std::tan(nakokulma / 2.0f);
    Mat4 r;
    r(0, 0) = t / suhde;
    r(1, 1) = t;
    r(2, 2) = (kauka + lahi) / (lahi - kauka);
    r(2, 3) = 2.0f * kauka * lahi / (lahi - kauka);
    r(3, 2) = -1.0f;
    return r;
}

// Ortografinen projektio laatikolle [-a, a]² × [lahi, kauka].
inline Mat4 orto(float a, float lahi, float kauka) {
    Mat4 r = Mat4::yksikko();
    r(0, 0) = r(1, 1) = 1.0f / a;
    r(2, 2) = -2.0f / (kauka - lahi);
    r(2, 3) = -(kauka + lahi) / (kauka - lahi);
    return r;
}

// Maailman piste kuvan pikseliksi (x, y ylhäältä) matriisilla mvp.
inline std::array<int, 2> pikseliksi(const Mat4& mvp, Vec3 p, int l,
                                     int k) {
    auto rivi = [&](int i) {
        return mvp(i, 0) * p.x + mvp(i, 1) * p.y + mvp(i, 2) * p.z +
               mvp(i, 3);
    };
    const float w = rivi(3);
    const float nx = rivi(0) / w, ny = rivi(1) / w;
    return {static_cast<int>((nx * 0.5f + 0.5f) * static_cast<float>(l)),
            static_cast<int>((0.5f - ny * 0.5f) * static_cast<float>(k))};
}
