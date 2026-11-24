/* Jonot, semaforit ja mutexit.
 *
 * Kaikki kolme ovat sama rakenne: jono kopioi alkiot omaan muistiinsa,
 * ja semafori on jono, jonka alkioilla ei ole sisältöä. Mutex on
 * binäärisemafori, jolla on omistaja; omistaja perii odottajan
 * prioriteetin (configUSE_PRIORITY_INHERITANCE). */
#include <string.h>

#include "kide_sisainen.h"

static void kopioi_sisaan(QueueHandle_t q, const void *alkio) {
    if (q->koko > 0) {
        memcpy(q->tila + q->kirjoitus * q->koko, alkio, q->koko);
        q->kirjoitus = (q->kirjoitus + 1) % q->pituus;
    }
    q->maara++;
}

static void kopioi_ulos(QueueHandle_t q, void *alkio) {
    if (q->koko > 0) {
        memcpy(alkio, q->tila + q->luku * q->koko, q->koko);
        q->luku = (q->luku + 1) % q->pituus;
    }
    q->maara--;
}

/* Paljonko aikarajasta on jäljellä; 0 = aika loppui. */
static TickType_t jaljella(TickType_t alku, TickType_t aikaraja) {
    if (aikaraja == portMAX_DELAY) {
        return portMAX_DELAY;
    }
    TickType_t kulunut = xTaskGetTickCount() - alku;
    return kulunut >= aikaraja ? 0 : aikaraja - kulunut;
}

QueueHandle_t xQueueCreateStatic(UBaseType_t pituus, UBaseType_t koko,
                                 uint8_t *tila, StaticQueue_t *q) {
    configASSERT(pituus > 0);
    configASSERT(koko == 0 || tila != NULL);
    memset(q, 0, sizeof *q);
    q->tila = tila;
    q->pituus = pituus;
    q->koko = koko;
    lista_alusta(&q->lahettajat);
    lista_alusta(&q->vastaanottajat);
    return q;
}

// @alku laheta
BaseType_t xQueueSend(QueueHandle_t q, const void *alkio,
                      TickType_t aikaraja) {
    TickType_t alku = xTaskGetTickCount();
    for (;;) {
        portti_kriittinen_alku();
        if (q->maara < q->pituus) {
            kopioi_sisaan(q, alkio);
            if (kide_heraa(&q->vastaanottajat)) {
                portti_vaihda();   /* odottaja on meitä tärkeämpi */
            }
            portti_kriittinen_loppu();
            return pdPASS;
        }
        TickType_t jaljella_nyt = jaljella(alku, aikaraja);
        if (jaljella_nyt == 0) {
            portti_kriittinen_loppu();
            return pdFAIL;     /* FreeRTOS: errQUEUE_FULL */
        }
        kide_odota(&q->lahettajat, jaljella_nyt);
        portti_kriittinen_loppu();
        /* Herättiin: tilaa vapautui tai aika loppui. Yritä uudelleen;
         * tärkeämpi tehtävä on voinut ehtiä ensin. */
    }
}
// @loppu laheta

// @alku vastaanota
BaseType_t xQueueReceive(QueueHandle_t q, void *alkio,
                         TickType_t aikaraja) {
    TickType_t alku = xTaskGetTickCount();
    for (;;) {
        portti_kriittinen_alku();
        if (q->maara > 0) {
            kopioi_ulos(q, alkio);
            if (q->mutex) {
                q->omistaja = kide_nykyinen;
                kide_nykyinen->mutexeja++;
            }
            if (kide_heraa(&q->lahettajat)) {
                portti_vaihda();
            }
            portti_kriittinen_loppu();
            return pdPASS;
        }
        TickType_t jaljella_nyt = jaljella(alku, aikaraja);
        if (jaljella_nyt == 0) {
            portti_kriittinen_loppu();
            return pdFAIL;     /* FreeRTOS: errQUEUE_EMPTY */
        }
#if configUSE_PRIORITY_INHERITANCE
        if (q->mutex && q->omistaja != NULL) {
            kide_peri_prioriteetti(q->omistaja);
        }
#endif
        kide_odota(&q->vastaanottajat, jaljella_nyt);
        portti_kriittinen_loppu();
    }
}
// @loppu vastaanota

// @alku isr
BaseType_t xQueueSendFromISR(QueueHandle_t q, const void *alkio,
                             BaseType_t *heratti) {
    portti_tarkista_isr();
    uint32_t vanha = portti_peita_isr();
    BaseType_t tulos = pdFAIL;
    if (q->maara < q->pituus) {   /* keskeytys ei voi jäädä odottamaan */
        kopioi_sisaan(q, alkio);
        if (kide_heraa(&q->vastaanottajat) && heratti != NULL) {
            *heratti = pdTRUE;     /* vaihto vasta käsittelijän lopussa */
        }
        tulos = pdPASS;
    }
    portti_palauta_isr(vanha);
    return tulos;
}
// @loppu isr

UBaseType_t uxQueueMessagesWaiting(QueueHandle_t q) {
    return q->maara;
}

// @alku luonti
SemaphoreHandle_t xSemaphoreCreateBinaryStatic(StaticSemaphore_t *s) {
    return xQueueCreateStatic(1, 0, NULL, s);   /* alkaa tyhjänä */
}

SemaphoreHandle_t xSemaphoreCreateCountingStatic(UBaseType_t enintaan,
                                                 UBaseType_t alku,
                                                 StaticSemaphore_t *s) {
    configASSERT(alku <= enintaan);
    xQueueCreateStatic(enintaan, 0, NULL, s);
    s->maara = alku;
    return s;
}

SemaphoreHandle_t xSemaphoreCreateMutexStatic(StaticSemaphore_t *s) {
    xQueueCreateStatic(1, 0, NULL, s);
    s->mutex = 1;
    s->maara = 1;                                 /* alkaa vapaana */
    return s;
}
// @loppu luonti

BaseType_t xSemaphoreTake(SemaphoreHandle_t s, TickType_t aikaraja) {
    return xQueueReceive(s, NULL, aikaraja);
}

// @alku anna
BaseType_t xSemaphoreGive(SemaphoreHandle_t s) {
    if (!s->mutex) {
        return xQueueSend(s, NULL, 0);
    }
    portti_kriittinen_alku();
    configASSERT(s->omistaja == kide_nykyinen);  /* vain haltija vapauttaa */
    BaseType_t vaihda = pdFALSE;
    s->omistaja = NULL;
    if (--kide_nykyinen->mutexeja == 0) {
        vaihda = kide_palauta_prioriteetti(kide_nykyinen);
    }
    kopioi_sisaan(s, NULL);
    if (kide_heraa(&s->vastaanottajat)) {
        vaihda = pdTRUE;
    }
    if (vaihda) {
        portti_vaihda();
    }
    portti_kriittinen_loppu();
    return pdPASS;
}
// @loppu anna

BaseType_t xSemaphoreGiveFromISR(SemaphoreHandle_t s, BaseType_t *heratti) {
    configASSERT(!s->mutex);   /* mutexilla on omistaja, ISR:llä ei */
    return xQueueSendFromISR(s, NULL, heratti);
}
