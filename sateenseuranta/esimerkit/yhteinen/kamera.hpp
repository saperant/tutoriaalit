// Neulanreikäkamera: säde jokaisen pikselin läpi.
#pragma once
#include "sade.hpp"

// @alku kamera
// Kamera katsoo silmästä kohdetta kohti. f = 1 / tan(fov / 2) kuten
// perspektiivimatriisissa; ruudun y kasvaa alaspäin.
struct Kamera {
    Vec3 silma, oikea, ylos, eteen;
    double f;
    int leveys, korkeus;

    // Säde pikselikoordinaatin (px, py) kautta; pikselin (x, y)
    // keskipiste on (x + 0.5, y + 0.5).
    Sade sade(double px, double py) const {
        double suhde = static_cast<double>(leveys) / korkeus;
        double sx = (2 * px / leveys - 1) * suhde;
        double sy = 1 - 2 * py / korkeus;
        return {silma, normalisoi(sx * oikea + sy * ylos + f * eteen)};
    }
};

inline Kamera kamera(Vec3 silma, Vec3 kohde, Vec3 ylos, double f,
                     int leveys, int korkeus) {
    Vec3 eteen = normalisoi(kohde - silma);
    Vec3 oikea = normalisoi(risti(eteen, ylos));
    return {silma, oikea, risti(oikea, eteen), eteen, f, leveys, korkeus};
}
// @loppu kamera
