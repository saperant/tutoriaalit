// Yksikkökvaternio kiertona ja TRS-muunnos (siirto, kierto, skaalaus).
#pragma once
#include "vektori.hpp"

// @alku kvaternio
// Kierto kulman k verran yksikköakselin u ympäri:
// q = (cos(k/2), sin(k/2) u). Oletusarvo on "ei kiertoa".
struct Kvat {
    double w = 1, x = 0, y = 0, z = 0;
};
inline Kvat akselikulma(Vec3 akseli, double kulma) {
    double s = std::sin(kulma / 2);
    return {std::cos(kulma / 2), s * akseli.x, s * akseli.y, s * akseli.z};
}
// Tulo a * b kiertää ensin b:llä ja sitten a:lla, kuten matriisit.
inline Kvat operator*(Kvat a, Kvat b) {
    return {a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
            a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
            a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
            a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w};
}
// Yksikkökvaternion käänteiskierto on liittoluku.
inline Kvat liitto(Kvat q) { return {q.w, -q.x, -q.y, -q.z}; }
inline double piste(Kvat a, Kvat b) {
    return a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z;
}
inline Kvat normalisoi(Kvat q) {
    double k = 1.0 / std::sqrt(piste(q, q));
    return {k * q.w, k * q.x, k * q.y, k * q.z};
}
// @loppu kvaternio

// @alku kierra
// Vektorin kierto ilman matriisia: v' = v + 2w(u x v) + 2u x (u x v),
// missä u on kvaternion vektoriosa.
inline Vec3 kierra(Kvat q, Vec3 v) {
    Vec3 u{q.x, q.y, q.z};
    Vec3 t = 2.0 * risti(u, v);
    return v + q.w * t + risti(u, t);
}
inline Mat4 matriisiksi(Kvat q) {
    Mat4 a = yksikko();
    Vec3 akselit[3] = {kierra(q, {1, 0, 0}), kierra(q, {0, 1, 0}),
                       kierra(q, {0, 0, 1})};
    for (int j = 0; j < 3; ++j) {  // kierretyt kanta-akselit sarakkeiksi
        a.m[0][j] = akselit[j].x;
        a.m[1][j] = akselit[j].y;
        a.m[2][j] = akselit[j].z;
    }
    return a;
}
// @loppu kierra

// @alku suuntaan
// Lyhin kierto, joka vie yksikkövektorin a yksikkövektoriksi b.
// Vastakkaisille vektoreille akseliksi kelpaa mikä tahansa kohtisuora.
inline Kvat kierto_suuntaan(Vec3 a, Vec3 b) {
    double c = piste(a, b);
    if (c < -0.999999) {
        Vec3 apu = std::abs(a.x) < 0.9 ? Vec3{1, 0, 0} : Vec3{0, 1, 0};
        return akselikulma(normalisoi(risti(a, apu)), PII);
    }
    Vec3 akseli = risti(a, b);
    return normalisoi(Kvat{1 + c, akseli.x, akseli.y, akseli.z});
}
// @loppu suuntaan

// @alku euler
// Eulerin kulmat kvaternioksi pelien tavallisessa järjestyksessä:
// kääntö y-akselin, nyökkäys x-akselin ja kallistus z-akselin ympäri.
// Kallistus tehdään ensin, kääntö viimeisenä.
inline Kvat eulerista(double kaanto, double nyokkays, double kallistus) {
    return akselikulma({0, 1, 0}, kaanto) *
           akselikulma({1, 0, 0}, nyokkays) *
           akselikulma({0, 0, 1}, kallistus);
}
// @loppu euler

// @alku matriisista
// Kiertomatriisin 3x3-osa kvaternioksi. Jäljen mukaan valitaan suurin
// komponentti jakajaksi, jotta jako ei osu lähelle nollaa.
inline Kvat matriisista(const Mat4& a) {
    const auto& m = a.m;
    double jalki = m[0][0] + m[1][1] + m[2][2];
    Kvat q;
    if (jalki > 0) {
        double s = 2 * std::sqrt(jalki + 1);
        q = {s / 4, (m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s,
             (m[1][0] - m[0][1]) / s};
    } else if (m[0][0] > m[1][1] && m[0][0] > m[2][2]) {
        double s = 2 * std::sqrt(1 + m[0][0] - m[1][1] - m[2][2]);
        q = {(m[2][1] - m[1][2]) / s, s / 4, (m[0][1] + m[1][0]) / s,
             (m[0][2] + m[2][0]) / s};
    } else if (m[1][1] > m[2][2]) {
        double s = 2 * std::sqrt(1 + m[1][1] - m[0][0] - m[2][2]);
        q = {(m[0][2] - m[2][0]) / s, (m[0][1] + m[1][0]) / s, s / 4,
             (m[1][2] + m[2][1]) / s};
    } else {
        double s = 2 * std::sqrt(1 + m[2][2] - m[0][0] - m[1][1]);
        q = {(m[1][0] - m[0][1]) / s, (m[0][2] + m[2][0]) / s,
             (m[1][2] + m[2][1]) / s, s / 4};
    }
    return normalisoi(q);
}
// @loppu matriisista

// @alku slerp
// Normalisoitu lineaarinen interpolointi: halpa, oikea reitti, mutta
// kulmanopeus ei ole vakio.
inline Kvat nlerp(Kvat a, Kvat b, double t) {
    if (piste(a, b) < 0) b = {-b.w, -b.x, -b.y, -b.z};  // lyhyempi kaari
    return normalisoi({a.w + t * (b.w - a.w), a.x + t * (b.x - a.x),
                       a.y + t * (b.y - a.y), a.z + t * (b.z - a.z)});
}
// Pallolineaarinen interpolointi: vakiokulmanopeus lyhintä kaarta.
inline Kvat slerp(Kvat a, Kvat b, double t) {
    double c = piste(a, b);
    if (c < 0) {  // q ja -q ovat sama kierto: valitaan lähempi
        b = {-b.w, -b.x, -b.y, -b.z};
        c = -c;
    }
    if (c > 0.9995) return nlerp(a, b, t);  // sin(kulma) lähes nolla
    double kulma = std::acos(c), s = std::sin(kulma);
    double ka = std::sin((1 - t) * kulma) / s;
    double kb = std::sin(t * kulma) / s;
    return {ka * a.w + kb * b.w, ka * a.x + kb * b.x, ka * a.y + kb * b.y,
            ka * a.z + kb * b.z};
}
// @loppu slerp

// @alku muunnos
// Solmun paikallinen muunnos osina. Osat voi animoida ja interpoloida
// erikseen; matriisi lasketaan niistä vasta käytettäessä.
struct Muunnos {
    Vec3 sijainti;
    Kvat kierto;
    Vec3 skaala{1, 1, 1};
};
// Järjestys: ensin skaalaus, sitten kierto, viimeisenä siirto.
inline Mat4 matriisi(const Muunnos& t) {
    return siirto(t.sijainti) * matriisiksi(t.kierto) * skaalaus(t.skaala);
}
inline Muunnos sekoita(const Muunnos& a, const Muunnos& b, double t) {
    return {lerp(a.sijainti, b.sijainti, t), slerp(a.kierto, b.kierto, t),
            lerp(a.skaala, b.skaala, t)};
}
// @loppu muunnos

// @alku hajota
// Matriisi takaisin osiksi. Toimii, kun matriisissa ei ole leikkausta
// (shear) eikä peilausta: sarakkeiden pituudet ovat skaalat.
inline Muunnos hajota(const Mat4& a) {
    Muunnos t;
    t.sijainti = {a.m[0][3], a.m[1][3], a.m[2][3]};
    Mat4 r = yksikko();
    double s[3];
    for (int j = 0; j < 3; ++j) {
        s[j] = pituus({a.m[0][j], a.m[1][j], a.m[2][j]});
        for (int i = 0; i < 3; ++i) r.m[i][j] = a.m[i][j] / s[j];
    }
    t.skaala = {s[0], s[1], s[2]};
    t.kierto = matriisista(r);
    return t;
}
// @loppu hajota
