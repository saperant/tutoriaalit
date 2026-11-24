/* Muistipooli (ks. pooli.h). */
#include "pooli.h"

// @alku pooli
void pooli_alusta(pooli_t *pooli, void *muisti, size_t lohkon_koko,
                  size_t lohkoja) {
    configASSERT(lohkon_koko >= sizeof(lohko_t) && lohkon_koko % 8 == 0);
    pooli->muisti = muisti;
    pooli->lohkon_koko = lohkon_koko;
    pooli->lohkoja = lohkoja;
    pooli->vapaat = NULL;
    for (size_t i = lohkoja; i > 0; i--) {   /* lista osoitejärjestykseen */
        lohko_t *lohko = (lohko_t *)(pooli->muisti + (i - 1) * lohkon_koko);
        lohko->seuraava = pooli->vapaat;
        pooli->vapaat = lohko;
    }
    pooli->laskuri = xSemaphoreCreateCountingStatic(
        lohkoja, lohkoja, &pooli->laskuri_tila);
}

void *pooli_varaa(pooli_t *pooli, TickType_t aikaraja) {
    if (xSemaphoreTake(pooli->laskuri, aikaraja) != pdPASS) {
        return NULL;                   /* ei vapautunut ajoissa */
    }
    taskENTER_CRITICAL();
    lohko_t *lohko = pooli->vapaat;    /* semafori takaa, ettei NULL */
    pooli->vapaat = lohko->seuraava;
    taskEXIT_CRITICAL();
    return lohko;
}

void pooli_vapauta(pooli_t *pooli, void *osoite) {
    uint8_t *p = osoite;
    size_t siirto = (size_t)(p - pooli->muisti);
    /* Vieras tai väärin kohdistettu osoite on ohjelmointivirhe. */
    configASSERT(p >= pooli->muisti &&
                 siirto < pooli->lohkoja * pooli->lohkon_koko &&
                 siirto % pooli->lohkon_koko == 0);
    taskENTER_CRITICAL();
    lohko_t *lohko = osoite;
    lohko->seuraava = pooli->vapaat;
    pooli->vapaat = lohko;
    taskEXIT_CRITICAL();
    xSemaphoreGive(pooli->laskuri);
}
// @loppu pooli

size_t pooli_vapaana(pooli_t *pooli) {
    return uxQueueMessagesWaiting(pooli->laskuri);
}
