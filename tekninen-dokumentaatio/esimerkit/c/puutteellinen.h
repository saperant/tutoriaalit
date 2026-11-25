/**
 * @file puutteellinen.h
 * @brief Esimerkki otsakkeesta, jonka kommentit eivät vastaa koodia.
 */
#ifndef PUUTTEELLINEN_H
#define PUUTTEELLINEN_H

/**
 * @brief Muuntaa anturin raaka-arvon celsiusasteiksi.
 * @param raaka AD-muuntimen lukema.
 * @return Lämpötila celsiusasteina.
 */
float muunna(int raaka_arvo, float kerroin);

float kalibroi(float lampotila);

#endif
