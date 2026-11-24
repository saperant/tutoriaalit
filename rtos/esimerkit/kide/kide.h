/* Kide: pieni opetuskäyttöön tehty reaaliaikaydin.
 *
 * Rajapinta jäljittelee FreeRTOSia: funktioiden nimet, parametrit ja
 * paluuarvot ovat samat niiltä osin kuin ne on toteutettu, joten
 * esimerkit kääntyvät pienin muutoksin myös FreeRTOSilla. Kaikki
 * oliot varataan staattisesti kutsujan muistista (FreeRTOSin
 * ...CreateStatic-funktiot); dynaaminen varaus on luvussa 10. */
#ifndef KIDE_H
#define KIDE_H

#include <stddef.h>
#include <stdint.h>

#include "kide_asetukset.h"
#include "lista.h"
#include "portti.h"

// @alku perustyypit
typedef uint32_t TickType_t;
typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
typedef uint32_t EventBits_t;

#define pdFALSE       ((BaseType_t)0)
#define pdTRUE        ((BaseType_t)1)
#define pdPASS        pdTRUE
#define pdFAIL        pdFALSE
#define portMAX_DELAY ((TickType_t)0xFFFFFFFFu)
#define pdMS_TO_TICKS(ms) \
    ((TickType_t)((uint64_t)(ms) * configTICK_RATE_HZ / 1000u))
// @loppu perustyypit

/* Väite: virhe ohjelmassa, ei ajonaikainen tilanne. */
#define configASSERT(ehto) \
    do { if (!(ehto)) kide_vaite(#ehto, __func__); } while (0)
_Noreturn void kide_vaite(const char *ehto, const char *funktio);

// @alku tcb
/* Tehtävän ohjauslohko (TCB, Task Control Block). */
typedef struct tcb {
    StackType_t *pino_osoitin;   /* oltava ensimmäinen: ks. PendSV */
    solmu_t tila_solmu;          /* valmis- tai viivelistassa */
    solmu_t odotus_solmu;        /* jonon tai semaforin odottajana */
    StackType_t *pino_pohja;     /* pinon alin osoite */
    uint32_t pino_sanat;
    UBaseType_t prioriteetti;    /* nykyinen, voi olla peritty */
    UBaseType_t perusprioriteetti;
    UBaseType_t mutexeja;        /* hallussa olevat mutexit */
    TaskFunction_t funktio;
    void *parametri;
    const char *nimi;
    volatile uint32_t ajoaika;   /* tikit, joiden aikana tehtävä ajoi */
    uint32_t vaihdot;            /* montako kertaa tehtävä on valittu */
    volatile uint32_t ilmoitus;  /* tehtäväilmoituksen arvo */
    uint8_t odottaa_ilmoitusta;
    uint8_t heratetty;           /* herätti tapahtuma, ei aikaraja */
    EventBits_t odotetut_bitit;  /* tapahtumaryhmän odotus */
    EventBits_t saadut_bitit;    /* bitit herätyshetkellä */
    uint8_t odota_kaikkia;
    uint8_t tyhjenna_bitit;
    PORTTI_TCB_KENTAT
} StaticTask_t;
// @loppu tcb

typedef StaticTask_t *TaskHandle_t;

// @alku jono
/* Jono. Semaforit ja mutexit ovat jonoja, joiden alkion koko on 0:
 * jäljellä on pelkkä laskuri ja odotuslistat (kuten FreeRTOSissa). */
typedef struct jono {
    uint8_t *tila;               /* alkioiden muisti */
    UBaseType_t pituus;          /* alkioiden enimmäismäärä */
    UBaseType_t koko;            /* alkion koko tavuina */
    volatile UBaseType_t maara;  /* alkioita nyt */
    UBaseType_t luku, kirjoitus; /* rengaspuskurin indeksit */
    lista_t lahettajat;          /* odottavat tilaa, prioriteetti-
                                    järjestyksessä */
    lista_t vastaanottajat;      /* odottavat alkiota */
    TaskHandle_t omistaja;       /* mutexin haltija tai NULL */
    uint8_t mutex;
} StaticQueue_t;
// @loppu jono

typedef StaticQueue_t *QueueHandle_t;
typedef StaticQueue_t *SemaphoreHandle_t;
typedef StaticQueue_t StaticSemaphore_t;

typedef struct {
    volatile EventBits_t bitit;
    lista_t odottajat;
} StaticEventGroup_t;
typedef StaticEventGroup_t *EventGroupHandle_t;

// @alku tehtavat
TaskHandle_t xTaskCreateStatic(TaskFunction_t funktio, const char *nimi,
                               uint32_t pino_sanat, void *parametri,
                               UBaseType_t prioriteetti,
                               StackType_t *pino, StaticTask_t *tcb);
BaseType_t xTaskCreate(TaskFunction_t funktio, const char *nimi,
                       uint32_t pino_sanat, void *parametri,
                       UBaseType_t prioriteetti, TaskHandle_t *kahva);
_Noreturn void vTaskStartScheduler(void);
void vTaskDelay(TickType_t tikit);
void vTaskDelayUntil(TickType_t *edellinen, TickType_t jakso);
TickType_t xTaskGetTickCount(void);
TaskHandle_t xTaskGetCurrentTaskHandle(void);
void taskYIELD(void);
UBaseType_t uxTaskPriorityGet(TaskHandle_t tehtava);
uint32_t ulTaskGetRunTimeCounter(TaskHandle_t tehtava);
uint32_t uxTaskGetStackHighWaterMark(TaskHandle_t tehtava);
const char *pcTaskGetName(TaskHandle_t tehtava);
// @loppu tehtavat

// @alku ilmoitukset
BaseType_t xTaskNotifyGive(TaskHandle_t tehtava);
void vTaskNotifyGiveFromISR(TaskHandle_t tehtava, BaseType_t *heratti);
uint32_t ulTaskNotifyTake(BaseType_t tyhjenna, TickType_t aikaraja);
// @loppu ilmoitukset

// @alku jonot
QueueHandle_t xQueueCreateStatic(UBaseType_t pituus, UBaseType_t koko,
                                 uint8_t *tila, StaticQueue_t *jono);
BaseType_t xQueueSend(QueueHandle_t jono, const void *alkio,
                      TickType_t aikaraja);
BaseType_t xQueueReceive(QueueHandle_t jono, void *alkio,
                         TickType_t aikaraja);
BaseType_t xQueueSendFromISR(QueueHandle_t jono, const void *alkio,
                             BaseType_t *heratti);
UBaseType_t uxQueueMessagesWaiting(QueueHandle_t jono);
// @loppu jonot

// @alku semaforit
SemaphoreHandle_t xSemaphoreCreateBinaryStatic(StaticSemaphore_t *s);
SemaphoreHandle_t xSemaphoreCreateCountingStatic(UBaseType_t enintaan,
                                                 UBaseType_t alku,
                                                 StaticSemaphore_t *s);
SemaphoreHandle_t xSemaphoreCreateMutexStatic(StaticSemaphore_t *s);
BaseType_t xSemaphoreTake(SemaphoreHandle_t s, TickType_t aikaraja);
BaseType_t xSemaphoreGive(SemaphoreHandle_t s);
BaseType_t xSemaphoreGiveFromISR(SemaphoreHandle_t s, BaseType_t *heratti);
// @loppu semaforit

// @alku tapahtumat
EventGroupHandle_t xEventGroupCreateStatic(StaticEventGroup_t *ryhma);
EventBits_t xEventGroupSetBits(EventGroupHandle_t ryhma, EventBits_t bitit);
EventBits_t xEventGroupWaitBits(EventGroupHandle_t ryhma,
                                EventBits_t bitit, BaseType_t tyhjenna,
                                BaseType_t kaikki, TickType_t aikaraja);
EventBits_t xEventGroupGetBits(EventGroupHandle_t ryhma);
// @loppu tapahtumat

// @alku muisti
void *pvPortMalloc(size_t koko);
size_t xPortGetFreeHeapSize(void);
// @loppu muisti

/* Keskeytyskäsittelijän lopussa: vaihda tehtävää, jos FromISR-kutsu
 * herätti nykyistä tärkeämmän tehtävän. */
#define portYIELD_FROM_ISR(heratti) \
    do { if (heratti) portti_vaihda(); } while (0)

/* Kriittiset osiot (FreeRTOS: taskENTER_CRITICAL ym.). */
#define taskENTER_CRITICAL() portti_kriittinen_alku()
#define taskEXIT_CRITICAL()  portti_kriittinen_loppu()

/* Kuluttaa prosessoriaikaa: esimerkkien laskentatyö. */
#define kide_kuormita(tikit) portti_kuormita(tikit)

/* Sovelluksen koukut; ytimessä on heikot oletustoteutukset. */
void vApplicationStackOverflowHook(TaskHandle_t tehtava, const char *nimi);
void vApplicationIdleHook(void);
void vApplicationTickHook(void);   /* tikkikeskeytyksestä */

#endif
