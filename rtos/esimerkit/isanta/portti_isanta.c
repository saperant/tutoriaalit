/* Isäntäportti: Kide-ydin Linux-prosessina (vrt. FreeRTOSin
 * POSIX-portti).
 *
 * Jokainen tehtävä on ucontext-konteksti omalla pinollaan, ja
 * tehtävänvaihto on swapcontext-kutsu. Keskeytyksiä ei ole: tikki
 * on simuloitu, ja se etenee vain, kun tehtävä kuluttaa laskenta-
 * aikaa (portti_kuormita) tai kun idle-tehtävä odottaa. Siksi ajo on
 * täysin deterministinen ja yhtä nopea kuin kone sallii, ja tulosteen
 * pitää olla sama kuin QEMU:ssa. */
#include <stdio.h>
#include <stdlib.h>

#include "kide_sisainen.h"

// @alku tila
#define PINO_TAVUINA (256u * 1024u)   /* isäntäkoneen printf tarvitsee
                                         enemmän kuin Cortex-M:n pino */
static uint32_t sisakkaisyys;       /* kriittisten osioiden syvyys */
static BaseType_t vaihto_odottaa;   /* PendSV:n vastine */
static BaseType_t tikissa;          /* "keskeytyskäsittelijässä" */
// @loppu tila

static void aloita(void) {
    TaskHandle_t t = kide_nykyinen;
    t->funktio(t->parametri);
    kide_tehtava_palasi();
}

StackType_t *portti_alusta_pino(struct tcb *tcb, StackType_t *huippu) {
    /* Tehtävän oma pino on liian pieni isäntäkoneelle: varataan uusi.
     * Ohjelma ei vapauta tehtäviä, joten pinoakaan ei vapauteta. */
    void *pino = malloc(PINO_TAVUINA);
    if (pino == NULL || getcontext(&tcb->konteksti) != 0) {
        perror("portti_alusta_pino");
        exit(1);
    }
    tcb->konteksti.uc_stack.ss_sp = pino;
    tcb->konteksti.uc_stack.ss_size = PINO_TAVUINA;
    tcb->konteksti.uc_link = NULL;
    makecontext(&tcb->konteksti, aloita, 0);
    return huippu;   /* ei käytetä: pinon tarkistus pysyy ehjänä */
}

// @alku vaihto
static void suorita_vaihto(void) {
    vaihto_odottaa = pdFALSE;
    TaskHandle_t vanha = kide_nykyinen;
    kide_valitse_seuraava();
    if (kide_nykyinen != vanha) {
        swapcontext(&vanha->konteksti, &kide_nykyinen->konteksti);
    }
}

void portti_vaihda(void) {
    vaihto_odottaa = pdTRUE;
    if (sisakkaisyys == 0 && !tikissa) {
        suorita_vaihto();
    }
}

void portti_kriittinen_alku(void) {
    sisakkaisyys++;
}

void portti_kriittinen_loppu(void) {
    if (--sisakkaisyys == 0 && vaihto_odottaa && !tikissa) {
        suorita_vaihto();
    }
}

/* Simuloitu tikkikeskeytys. */
static void tikki(void) {
    tikissa = pdTRUE;
    if (kide_tikki()) {
        vaihto_odottaa = pdTRUE;
    }
    tikissa = pdFALSE;
    if (vaihto_odottaa && sisakkaisyys == 0) {
        suorita_vaihto();
    }
}
// @loppu vaihto

_Noreturn void portti_kaynnista(void) {
    setcontext(&kide_nykyinen->konteksti);
    perror("setcontext");
    exit(1);
}

uint32_t portti_peita_isr(void) {
    return 0;
}

void portti_palauta_isr(uint32_t vanha) {
    (void)vanha;
}

void portti_tarkista_isr(void) {}

// @alku kuormita
void portti_kuormita(uint32_t tikit) {
    TaskHandle_t t = kide_nykyinen;
    uint32_t alku = t->ajoaika;
    while (t->ajoaika - alku < tikit) {
        tikki();   /* kirjaa tikin tälle tehtävälle, voi vaihtaa */
    }
}

void portti_odota(void) {
    tikki();       /* idle: aika hyppää suoraan seuraavaan tikkiin */
}
// @loppu kuormita
