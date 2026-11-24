/* Tehtävät, vuorontaja ja tikki. */
#include <string.h>

#include "kide_sisainen.h"
#include "konsoli.h"
#include "semihost.h"

#define PINON_VARTIJA 0xA5A5A5A5u

// @alku tila
static lista_t valmiit[configMAX_PRIORITIES]; /* yksi lista/prioriteetti */
static volatile uint32_t valmiit_bitit;       /* bitti p: valmiit[p]
                                                 ei ole tyhjä */
static lista_t viivastetyt;    /* herätystikin mukaan järjestetty */
static volatile TickType_t tikit;
static volatile BaseType_t ajossa;
static BaseType_t vaihto_kesken; /* herätetty tärkeämpi odottaa vaihtoa
                                    (FreeRTOS: xYieldPending) */
TaskHandle_t volatile kide_nykyinen;
// @loppu tila

static StaticTask_t idle_tcb;
static StackType_t idle_pino[configMINIMAL_STACK_SIZE];

static void alusta_listat(void) {
    static BaseType_t alustettu;
    if (!alustettu) {
        for (UBaseType_t p = 0; p < configMAX_PRIORITIES; p++) {
            lista_alusta(&valmiit[p]);
        }
        lista_alusta(&viivastetyt);
        alustettu = pdTRUE;
    }
}

// @alku valmiit
static void lisaa_valmiiksi(TaskHandle_t t) {
    lista_lisaa_loppuun(&valmiit[t->prioriteetti], &t->tila_solmu);
    valmiit_bitit |= 1u << t->prioriteetti;
}

static BaseType_t on_valmis(TaskHandle_t t) {
    return t->tila_solmu.lista != NULL && t->tila_solmu.lista != &viivastetyt;
}

static void poista_valmiista(TaskHandle_t t) {
    lista_poista(&t->tila_solmu);
    if (valmiit[t->prioriteetti].pituus == 0) {
        valmiit_bitit &= ~(1u << t->prioriteetti);
    }
}

/* Siirtää tehtävän prioriteettinsa jonon perälle (kiertovuorottelu). */
static BaseType_t siirra_peralle(TaskHandle_t t) {
    lista_t *oma = &valmiit[t->prioriteetti];
    if (!on_valmis(t) || oma->pituus < 2) {
        return pdFALSE;
    }
    lista_poista(&t->tila_solmu);
    lista_lisaa_loppuun(oma, &t->tila_solmu);
    return pdTRUE;
}
// @loppu valmiit

TaskHandle_t xTaskCreateStatic(TaskFunction_t funktio, const char *nimi,
                               uint32_t pino_sanat, void *parametri,
                               UBaseType_t prioriteetti,
                               StackType_t *pino, StaticTask_t *tcb) {
    configASSERT(prioriteetti < configMAX_PRIORITIES);
    configASSERT(pino_sanat >= 32u);
    memset(tcb, 0, sizeof *tcb);
    for (uint32_t i = 0; i < pino_sanat; i++) {
        pino[i] = PINON_VARTIJA;   /* käyttämätön pino tunnistetaan */
    }
    tcb->pino_pohja = pino;
    tcb->pino_sanat = pino_sanat;
    tcb->prioriteetti = prioriteetti;
    tcb->perusprioriteetti = prioriteetti;
    tcb->funktio = funktio;
    tcb->parametri = parametri;
    tcb->nimi = nimi;
    solmu_alusta(&tcb->tila_solmu, tcb);
    solmu_alusta(&tcb->odotus_solmu, tcb);
    tcb->pino_osoitin = portti_alusta_pino(tcb, pino + pino_sanat);

    portti_kriittinen_alku();
    alusta_listat();
    lisaa_valmiiksi(tcb);
    if (ajossa && prioriteetti > kide_nykyinen->prioriteetti) {
        portti_vaihda();
    }
    portti_kriittinen_loppu();
    return tcb;
}

BaseType_t xTaskCreate(TaskFunction_t funktio, const char *nimi,
                       uint32_t pino_sanat, void *parametri,
                       UBaseType_t prioriteetti, TaskHandle_t *kahva) {
    StaticTask_t *tcb = pvPortMalloc(sizeof *tcb);
    StackType_t *pino = pvPortMalloc(pino_sanat * sizeof *pino);
    if (tcb == NULL || pino == NULL) {
        return pdFAIL;   /* heap_1 ei vapauta: osittainen varaus jää */
    }
    TaskHandle_t t = xTaskCreateStatic(funktio, nimi, pino_sanat,
                                       parametri, prioriteetti, pino, tcb);
    if (kahva != NULL) {
        *kahva = t;
    }
    return pdPASS;
}

static void idle_tehtava(void *parametri) {
    (void)parametri;
    for (;;) {
        vApplicationIdleHook();
        portti_odota();
    }
}

__attribute__((weak)) void vApplicationIdleHook(void) {}
__attribute__((weak)) void vApplicationTickHook(void) {}

// @alku valinta
static TaskHandle_t tarkein_valmis(void) {
    /* Idle-tehtävä on aina valmis, joten bittikartta ei ole nolla.
     * CLZ-käsky laskee etunollat yhdellä käskyllä. */
    uint32_t p = 31u - (uint32_t)__builtin_clz(valmiit_bitit);
    return lista_ensimmainen(&valmiit[p])->omistaja;
}

void kide_valitse_seuraava(void) {
#if configCHECK_FOR_STACK_OVERFLOW
    TaskHandle_t t = kide_nykyinen;
    if (t->pino_osoitin < t->pino_pohja ||
        t->pino_pohja[0] != PINON_VARTIJA ||
        t->pino_pohja[1] != PINON_VARTIJA) {
        vApplicationStackOverflowHook(t, t->nimi);
    }
#endif
    vaihto_kesken = pdFALSE;
    TaskHandle_t seuraava = tarkein_valmis();
    if (seuraava != kide_nykyinen) {
        seuraava->vaihdot++;
        kide_nykyinen = seuraava;
    }
}
// @loppu valinta

_Noreturn void vTaskStartScheduler(void) {
    xTaskCreateStatic(idle_tehtava, "IDLE", configMINIMAL_STACK_SIZE,
                      NULL, 0, idle_pino, &idle_tcb);
    portti_kriittinen_alku();
    kide_nykyinen = tarkein_valmis();
    kide_nykyinen->vaihdot++;
    ajossa = pdTRUE;
    portti_kriittinen_loppu();
    portti_kaynnista();
}

// @alku tikki
BaseType_t kide_tikki(void) {
    BaseType_t vaihda = pdFALSE;
    tikit++;
    kide_nykyinen->ajoaika++;   /* koko tikin väli kirjataan ajajalle */
    vApplicationTickHook();
    /* Herätä tehtävät, joiden viive tai aikaraja on täynnä. */
    solmu_t *s;
    while ((s = lista_ensimmainen(&viivastetyt)) != NULL &&
           (int32_t)(s->arvo - tikit) <= 0) {
        TaskHandle_t t = s->omistaja;
        lista_poista(s);
        lista_poista(&t->odotus_solmu);   /* aikaraja: pois jonosta */
        t->odottaa_ilmoitusta = 0;
        lisaa_valmiiksi(t);
        if (t->prioriteetti > kide_nykyinen->prioriteetti) {
            vaihda = pdTRUE;
        }
    }
#if configUSE_TIME_SLICING
    /* Saman prioriteetin tehtävät vuorottelevat. */
    if (siirra_peralle(kide_nykyinen)) {
        vaihda = pdTRUE;
    }
#endif
    /* Keskeytys herätti tärkeämmän tehtävän mutta ei pyytänyt vaihtoa
     * (portYIELD_FROM_ISR puuttui): vaihda viimeistään nyt. */
    return vaihda || vaihto_kesken;
}
// @loppu tikki

// @alku odotus
void kide_odota(lista_t *odotuslista, TickType_t aikaraja) {
    TaskHandle_t t = kide_nykyinen;
    t->heratetty = pdFALSE;
    poista_valmiista(t);
    if (odotuslista != NULL) {
        /* Tärkein odottaja ensin: avain on käänteinen prioriteetti. */
        t->odotus_solmu.arvo = configMAX_PRIORITIES - t->prioriteetti;
        lista_lisaa_jarjestykseen(odotuslista, &t->odotus_solmu, 0);
    }
    if (aikaraja != portMAX_DELAY) {
        t->tila_solmu.arvo = tikit + aikaraja;
        lista_lisaa_jarjestykseen(&viivastetyt, &t->tila_solmu, tikit);
    }
    /* Ilman aikarajaa tehtävä ei ole missään tilalistassa: vain
     * tapahtuma voi herättää sen. */
    portti_vaihda();
}

BaseType_t kide_heraa_tehtava(TaskHandle_t t) {
    lista_poista(&t->odotus_solmu);
    lista_poista(&t->tila_solmu);      /* aikaraja ei enää koske */
    t->heratetty = pdTRUE;
    lisaa_valmiiksi(t);
    if (t->prioriteetti > kide_nykyinen->prioriteetti) {
        vaihto_kesken = pdTRUE;
        return pdTRUE;
    }
    return pdFALSE;
}

BaseType_t kide_heraa(lista_t *odotuslista) {
    solmu_t *s = lista_ensimmainen(odotuslista);
    return s == NULL ? pdFALSE : kide_heraa_tehtava(s->omistaja);
}
// @loppu odotus

// @alku periytys
static void aseta_prioriteetti(TaskHandle_t t, UBaseType_t uusi) {
    BaseType_t valmis = on_valmis(t);
    if (valmis) {
        poista_valmiista(t);
    }
    t->prioriteetti = uusi;
    if (valmis) {
        lisaa_valmiiksi(t);
    }
    lista_t *odotus = t->odotus_solmu.lista;
    if (odotus != NULL) {   /* järjestys odotuslistassa muuttuu */
        lista_poista(&t->odotus_solmu);
        t->odotus_solmu.arvo = configMAX_PRIORITIES - uusi;
        lista_lisaa_jarjestykseen(odotus, &t->odotus_solmu, 0);
    }
}

void kide_peri_prioriteetti(TaskHandle_t haltija) {
    if (haltija->prioriteetti < kide_nykyinen->prioriteetti) {
        aseta_prioriteetti(haltija, kide_nykyinen->prioriteetti);
    }
}

BaseType_t kide_palauta_prioriteetti(TaskHandle_t haltija) {
    if (haltija->prioriteetti == haltija->perusprioriteetti) {
        return pdFALSE;
    }
    aseta_prioriteetti(haltija, haltija->perusprioriteetti);
    return pdTRUE;
}
// @loppu periytys

// @alku viive
void vTaskDelay(TickType_t viive) {
    portti_kriittinen_alku();
    if (viive > 0) {
        kide_odota(NULL, viive);
    } else if (siirra_peralle(kide_nykyinen)) {
        portti_vaihda();   /* viive 0: anna vuoro saman prioriteetin */
    }
    portti_kriittinen_loppu();   /* tehtävänvaihto tapahtuu tässä */
}

void vTaskDelayUntil(TickType_t *edellinen, TickType_t jakso) {
    portti_kriittinen_alku();
    TickType_t herays = *edellinen + jakso;
    *edellinen = herays;
    if ((int32_t)(herays - tikit) > 0) {
        kide_odota(NULL, herays - tikit);
    }
    portti_kriittinen_loppu();
}
// @loppu viive

TickType_t xTaskGetTickCount(void) {
    return tikit;
}

TaskHandle_t xTaskGetCurrentTaskHandle(void) {
    return kide_nykyinen;
}

void taskYIELD(void) {
    portti_kriittinen_alku();
    if (siirra_peralle(kide_nykyinen)) {
        portti_vaihda();
    }
    portti_kriittinen_loppu();
}

UBaseType_t uxTaskPriorityGet(TaskHandle_t tehtava) {
    return tehtava->prioriteetti;
}

uint32_t ulTaskGetRunTimeCounter(TaskHandle_t tehtava) {
    return tehtava->ajoaika;
}

const char *pcTaskGetName(TaskHandle_t tehtava) {
    return tehtava->nimi;
}

// @alku vesiraja
uint32_t uxTaskGetStackHighWaterMark(TaskHandle_t tehtava) {
    /* Montako sanaa pinon pohjalta on yhä koskematta. */
    uint32_t vapaat = 0;
    while (vapaat < tehtava->pino_sanat &&
           tehtava->pino_pohja[vapaat] == PINON_VARTIJA) {
        vapaat++;
    }
    return vapaat;
}
// @loppu vesiraja

// @alku ilmoitus
BaseType_t xTaskNotifyGive(TaskHandle_t tehtava) {
    portti_kriittinen_alku();
    tehtava->ilmoitus++;
    if (tehtava->odottaa_ilmoitusta) {
        tehtava->odottaa_ilmoitusta = 0;
        if (kide_heraa_tehtava(tehtava)) {
            portti_vaihda();
        }
    }
    portti_kriittinen_loppu();
    return pdPASS;
}

void vTaskNotifyGiveFromISR(TaskHandle_t tehtava, BaseType_t *heratti) {
    portti_tarkista_isr();
    uint32_t vanha = portti_peita_isr();
    tehtava->ilmoitus++;
    if (tehtava->odottaa_ilmoitusta) {
        tehtava->odottaa_ilmoitusta = 0;
        if (kide_heraa_tehtava(tehtava) && heratti != NULL) {
            *heratti = pdTRUE;
        }
    }
    portti_palauta_isr(vanha);
}

uint32_t ulTaskNotifyTake(BaseType_t tyhjenna, TickType_t aikaraja) {
    TaskHandle_t t = kide_nykyinen;
    portti_kriittinen_alku();
    if (t->ilmoitus == 0 && aikaraja != 0) {
        t->odottaa_ilmoitusta = 1;
        kide_odota(NULL, aikaraja);
    }
    portti_kriittinen_loppu();   /* odotus tapahtuu tässä */

    portti_kriittinen_alku();
    uint32_t arvo = t->ilmoitus;
    if (arvo > 0) {
        t->ilmoitus = tyhjenna ? 0 : arvo - 1;
    }
    t->odottaa_ilmoitusta = 0;
    portti_kriittinen_loppu();
    return arvo;
}
// @loppu ilmoitus

/* Tehtäväfunktio ei saa palata: portti asettaa tämän paluuosoitteeksi. */
void kide_tehtava_palasi(void) {
    tulosta("VIRHE: tehtava %s palasi\n", kide_nykyinen->nimi);
    lopeta(98);
}

__attribute__((weak))
void vApplicationStackOverflowHook(TaskHandle_t tehtava, const char *nimi) {
    (void)tehtava;
    tulosta("PINON YLIVUOTO: %s\n", nimi);
    lopeta(97);
}

_Noreturn void kide_vaite(const char *ehto, const char *funktio) {
    portti_kriittinen_alku();
    tulosta("VAITE: %s (%s)\n", ehto, funktio);
    lopeta(96);
}
