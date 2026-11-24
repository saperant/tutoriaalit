/* Tapahtumaryhmät: tehtävä odottaa yhtä tai useaa bittiä. */
#include "kide_sisainen.h"

EventGroupHandle_t xEventGroupCreateStatic(StaticEventGroup_t *ryhma) {
    ryhma->bitit = 0;
    lista_alusta(&ryhma->odottajat);
    return ryhma;
}

static BaseType_t ehto_tayttyy(EventBits_t bitit, EventBits_t odotetut,
                               BaseType_t kaikki) {
    EventBits_t osuma = bitit & odotetut;
    return kaikki ? osuma == odotetut : osuma != 0;
}

// @alku aseta
EventBits_t xEventGroupSetBits(EventGroupHandle_t ryhma, EventBits_t bitit) {
    portti_kriittinen_alku();
    ryhma->bitit |= bitit;
    EventBits_t tyhjennettavat = 0;
    BaseType_t vaihda = pdFALSE;
    /* Käy läpi kaikki odottajat: jokaisella on oma ehtonsa. */
    solmu_t *s = ryhma->odottajat.vartija.seuraava;
    while (s != &ryhma->odottajat.vartija) {
        solmu_t *seuraava = s->seuraava;
        TaskHandle_t t = s->omistaja;
        if (ehto_tayttyy(ryhma->bitit, t->odotetut_bitit, t->odota_kaikkia)) {
            if (t->tyhjenna_bitit) {
                tyhjennettavat |= t->odotetut_bitit;
            }
            t->saadut_bitit = ryhma->bitit;
            if (kide_heraa_tehtava(t)) {
                vaihda = pdTRUE;
            }
        }
        s = seuraava;
    }
    ryhma->bitit &= ~tyhjennettavat;
    EventBits_t tulos = ryhma->bitit;
    if (vaihda) {
        portti_vaihda();
    }
    portti_kriittinen_loppu();
    return tulos;
}
// @loppu aseta

// @alku odota
EventBits_t xEventGroupWaitBits(EventGroupHandle_t ryhma,
                                EventBits_t bitit, BaseType_t tyhjenna,
                                BaseType_t kaikki, TickType_t aikaraja) {
    TaskHandle_t t = xTaskGetCurrentTaskHandle();
    portti_kriittinen_alku();
    EventBits_t tulos = ryhma->bitit;
    if (ehto_tayttyy(tulos, bitit, kaikki)) {
        if (tyhjenna) {
            ryhma->bitit &= ~bitit;
        }
        portti_kriittinen_loppu();
        return tulos;
    }
    if (aikaraja == 0) {
        portti_kriittinen_loppu();
        return tulos;
    }
    t->odotetut_bitit = bitit;
    t->odota_kaikkia = (uint8_t)kaikki;
    t->tyhjenna_bitit = (uint8_t)tyhjenna;
    kide_odota(&ryhma->odottajat, aikaraja);
    portti_kriittinen_loppu();          /* odotus tapahtuu tässä */

    portti_kriittinen_alku();
    tulos = t->heratetty ? t->saadut_bitit : ryhma->bitit;
    portti_kriittinen_loppu();
    return tulos;   /* kutsuja tarkistaa, täyttyikö ehto */
}
// @loppu odota

EventBits_t xEventGroupGetBits(EventGroupHandle_t ryhma) {
    return ryhma->bitit;
}
