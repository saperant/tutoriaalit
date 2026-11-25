/**
 * @file pino.h
 * @brief Kokonaislukupinon julkinen rajapinta.
 *
 * Pino ei ole säieturvallinen: samaa pinoa saa käsitellä vain yksi
 * säie kerrallaan.
 */
#ifndef PINO_H
#define PINO_H

#include <stddef.h>

/** Epätäydellinen tyyppi: käyttäjä näkee vain nimen, ei kenttiä. */
typedef struct pino Pino;

/**
 * @brief Luo tyhjän pinon.
 * @return Uusi pino tai nullptr, jos muisti loppui. Kutsuja omistaa
 *         pinon ja vapauttaa sen funktiolla pino_tuhoa().
 */
Pino *pino_luo(void);

/**
 * @brief Vapauttaa pinon ja sen alkiot.
 * @param p Tuhottava pino; nullptr on sallittu eikä tee mitään.
 */
void pino_tuhoa(Pino *p);

/**
 * @brief Lisää arvon pinon päälle.
 * @param p    Pino; ei saa olla nullptr.
 * @param arvo Lisättävä arvo.
 * @return true, jos lisäys onnistui; false, jos muisti loppui. Pino
 *         säilyy silloin ennallaan.
 */
bool pino_lisaa(Pino *p, int arvo);

/**
 * @brief Poistaa pinon päällimmäisen arvon.
 * @param p          Pino; ei saa olla nullptr.
 * @param[out] arvo  Poistettu arvo. Ei muutu, jos pino on tyhjä.
 * @return true, jos arvo saatiin; false, jos pino oli tyhjä.
 */
bool pino_ota(Pino *p, int *arvo);

/**
 * @brief Kertoo pinon koon.
 * @param p Pino; ei saa olla nullptr.
 * @return Pinossa olevien alkioiden määrä.
 */
size_t pino_koko(const Pino *p);

#endif
