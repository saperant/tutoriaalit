/**
 * @file puskuri.h
 * @brief Kiinteän kokoinen rengaspuskuri mittausarvoille.
 *
 * Puskuri säilyttää viimeisimmät arvot ja laskee niiden keskiarvon.
 * Muistia ei varata dynaamisesti, joten puskuri sopii laitteeseen,
 * jossa ei ole kekoa.
 */
#ifndef PUSKURI_H
#define PUSKURI_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @defgroup puskuri Rengaspuskuri
 * @brief Viimeisimpien mittausarvojen säilytys ja keskiarvo.
 *
 * Tyypillinen käyttö:
 * @code{.c}
 * struct puskuri p;
 * puskuri_alusta(&p);
 * puskuri_lisaa(&p, 21.5f);
 * float keskiarvo;
 * if (puskuri_keskiarvo(&p, &keskiarvo)) { ... }
 * @endcode
 * @{
 */

/** Puskuriin mahtuvien arvojen määrä. */
#define PUSKURI_KOKO 8

// @alku rakenne
/**
 * @brief Rengaspuskurin tila.
 *
 * Kenttiä ei muokata suoraan: käytä funktioita puskuri_alusta() ja
 * puskuri_lisaa(). Rakenne on näkyvissä vain, jotta sen voi varata
 * pinosta tai staattisesti.
 */
struct puskuri {
    float arvot[PUSKURI_KOKO]; /**< Arvot, vanhin kohdassa @ref alku. */
    size_t alku;               /**< Vanhimman arvon indeksi. */
    size_t maara;              /**< Tallessa olevien arvojen määrä. */
};
// @loppu rakenne

/**
 * @brief Tyhjentää puskurin.
 * @param[out] p Alustettava puskuri. Ei saa olla NULL.
 */
void puskuri_alusta(struct puskuri *p);

// @alku lisaa
/**
 * @brief Lisää arvon puskuriin.
 *
 * Kun puskuri on täynnä, uusi arvo korvaa vanhimman.
 *
 * @param[in,out] p    Puskuri, joka on alustettu funktiolla
 *                     puskuri_alusta().
 * @param[in]     arvo Lisättävä arvo.
 * @return true, jos vanhin arvo jouduttiin korvaamaan.
 */
bool puskuri_lisaa(struct puskuri *p, float arvo);
// @loppu lisaa

/**
 * @brief Laskee puskurin arvojen keskiarvon.
 *
 * @param[in]  p         Puskuri.
 * @param[out] keskiarvo Tulos. Arvoa ei muuteta, jos puskuri on tyhjä.
 * @retval true  Keskiarvo laskettiin.
 * @retval false Puskuri on tyhjä.
 * @note Aikavaativuus on O(PUSKURI_KOKO): summa lasketaan joka kerta
 *       uudelleen, jotta pyöristysvirhe ei kerry.
 */
bool puskuri_keskiarvo(const struct puskuri *p, float *keskiarvo);

/** @} */

#endif
