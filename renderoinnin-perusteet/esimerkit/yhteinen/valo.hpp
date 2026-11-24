// Valaistusmallit: Lambert, Phong ja Blinn-Phong.
#pragma once
#include <algorithm>
#include <cmath>

#include "kuva.hpp"
#include "vektori.hpp"

// @alku valo
struct Materiaali {
    Vari ymparisto;  // vakiovalo, joka korvaa epäsuoran valon
    Vari diffuusi;   // mattapinnan väri
    Vari peili;      // heijastuksen väri
    double kiilto;   // heijastuksen kapeus (eksponentti)
};

// Lambert: pinta saa valoa suhteessa kulman kosiniin. Kaikki vektorit
// ovat yksikkövektoreita; l osoittaa pinnasta valoa kohti.
inline double lambert(Vec3 n, Vec3 l) { return std::max(0.0, piste(n, l)); }

// Phong: heijastuneen säteen r ja katsesuunnan v kulma.
inline double phong(Vec3 n, Vec3 l, Vec3 v, double kiilto) {
    double nl = piste(n, l);
    if (nl <= 0) return 0;
    Vec3 r = 2 * nl * n - l;
    return std::pow(std::max(0.0, piste(r, v)), kiilto);
}

// Blinn-Phong: puolivälivektorin h = (l + v) / |l + v| ja normaalin
// kulma. Halvempi laskea ja käyttäytyy paremmin loivissa kulmissa.
inline double blinn_phong(Vec3 n, Vec3 l, Vec3 v, double kiilto) {
    if (piste(n, l) <= 0) return 0;
    Vec3 h = normalisoi(l + v);
    return std::pow(std::max(0.0, piste(n, h)), kiilto);
}

// Yhden valon varjostus: ympäristö + diffuusi + heijastus.
inline Vari varjosta(const Materiaali& m, Vec3 n, Vec3 l, Vec3 v,
                     Vari valo) {
    return m.ymparisto + lambert(n, l) * (m.diffuusi * valo) +
           blinn_phong(n, l, v, m.kiilto) * (m.peili * valo);
}
// @loppu valo
