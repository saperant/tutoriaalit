/* Ohjelmistoajastimet. Kidessä niitä ei ole valmiina, joten esimerkki
 * rakentaa ne samalla tavalla kuin FreeRTOSin timers.c: ajastimet ovat
 * taulukossa, ja yksi tehtävä, ajastinpalvelu, odottaa komentojonossa
 * seuraavaan erääntymiseen asti ja kutsuu takaisinkutsut omassa
 * kontekstissaan. */
#include "kide.h"
#include "konsoli.h"
#include "semihost.h"

// @alku tyypit
typedef struct ajastin {
    const char *nimi;
    TickType_t jakso;                  /* 0: laukeaa kerran */
    void (*takaisinkutsu)(struct ajastin *ajastin, TickType_t myohassa);
    TickType_t eraantyy;
    int kaynnissa;
} ajastin_t;

typedef struct {                       /* komento palvelulle */
    ajastin_t *ajastin;
    TickType_t eraantyy;
} komento_t;

#define AJASTIMIA 3u
static ajastin_t *ajastimet[AJASTIMIA];
static unsigned ajastimia;
static uint8_t komentojen_muisti[4 * sizeof(komento_t)];
static StaticQueue_t komentojen_tila;
static QueueHandle_t komennot;
// @loppu tyypit

// @alku kaynnista
/* Kutsutaan mistä tahansa tehtävästä: ajastimen tilaa muuttaa vain
 * palvelu, joten lukkoja ei tarvita. */
static void ajastin_kaynnista(ajastin_t *ajastin, TickType_t viive) {
    komento_t komento = {ajastin, xTaskGetTickCount() + viive};
    BaseType_t ok = xQueueSend(komennot, &komento, portMAX_DELAY);
    configASSERT(ok == pdPASS);
}
// @loppu kaynnista

// @alku palvelu
/* Erotus etumerkillisenä toimii myös tikkilaskurin pyörähtäessä. */
static int32_t jaljella(const ajastin_t *ajastin, TickType_t nyt) {
    return (int32_t)(ajastin->eraantyy - nyt);
}

static void ajastinpalvelu(void *parametri) {
    (void)parametri;
    for (;;) {
        TickType_t nyt = xTaskGetTickCount();
        TickType_t odotus = portMAX_DELAY;
        for (unsigned i = 0; i < ajastimia; i++) {
            ajastin_t *a = ajastimet[i];
            if (!a->kaynnissa) {
                continue;
            }
            if (jaljella(a, nyt) <= 0) {           /* erääntynyt */
                if (a->jakso > 0) {
                    a->eraantyy += a->jakso;       /* vaihe säilyy */
                } else {
                    a->kaynnissa = 0;
                }
                a->takaisinkutsu(a, nyt - (a->eraantyy - a->jakso));
                odotus = 0;                        /* tarkista uudelleen */
            } else if ((TickType_t)jaljella(a, nyt) < odotus) {
                odotus = (TickType_t)jaljella(a, nyt);
            }
        }
        komento_t komento;
        if (xQueueReceive(komennot, &komento, odotus) == pdPASS) {
            komento.ajastin->eraantyy = komento.eraantyy;
            komento.ajastin->kaynnissa = 1;
        }
    }
}
// @loppu palvelu

static TaskHandle_t sovellus_kahva;

// @alku kutsut
static void vilkku_kutsu(ajastin_t *ajastin, TickType_t myohassa) {
    tulosta("%3u %s", xTaskGetTickCount(), ajastin->nimi);
    if (myohassa > 0) {
        tulosta(" (myohassa %u)", myohassa);
    }
    tulosta("\n");
}

/* Oikea tapa: takaisinkutsu vain herättää tehtävän, joka tekee työn. */
static void aikakatkaisu_kutsu(ajastin_t *ajastin, TickType_t myohassa) {
    (void)ajastin;
    (void)myohassa;
    xTaskNotifyGive(sovellus_kahva);
}

/* VIRHE: pitkä työ takaisinkutsussa pysäyttää kaikki muut ajastimet. */
static void hidas_kutsu(ajastin_t *ajastin, TickType_t myohassa) {
    (void)myohassa;
    tulosta("%3u %s alkaa\n", xTaskGetTickCount(), ajastin->nimi);
    kide_kuormita(7);
    tulosta("%3u %s valmis\n", xTaskGetTickCount(), ajastin->nimi);
}

static ajastin_t vilkku = {"vilkku", 5, vilkku_kutsu, 0, 0};
static ajastin_t aikakatkaisu = {"aikakatkaisu", 0, aikakatkaisu_kutsu, 0, 0};
static ajastin_t hidas = {"hidas takaisinkutsu", 0, hidas_kutsu, 0, 0};
// @loppu kutsut

// @alku sovellus
static void sovellus(void *parametri) {
    (void)parametri;
    ajastin_kaynnista(&vilkku, 5);
    tulosta("%3u sovellus: pyynto lahetetty, aikaraja 12\n",
            xTaskGetTickCount());
    ajastin_kaynnista(&aikakatkaisu, 12);
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);   /* vastaus tai ajastin */
    tulosta("%3u sovellus: vastausta ei tullut, aikakatkaisu\n",
            xTaskGetTickCount());
    ajastin_kaynnista(&hidas, 4);
    vTaskDelay(20);
    lopeta(0);
}
// @loppu sovellus

static StaticTask_t tcb[2];
static StackType_t pinot[2][256];

// @alku main
int main(void) {
    konsoli_alusta();
    komennot = xQueueCreateStatic(4, sizeof(komento_t), komentojen_muisti,
                                  &komentojen_tila);
    ajastimet[ajastimia++] = &vilkku;
    ajastimet[ajastimia++] = &aikakatkaisu;
    ajastimet[ajastimia++] = &hidas;
    /* Palvelun prioriteetti ratkaisee ajastimien tarkkuuden: sitä
     * tärkeämmät tehtävät viivästyttävät jokaista takaisinkutsua. */
    xTaskCreateStatic(ajastinpalvelu, "ajastimet", 256, NULL, 3, pinot[0],
                      &tcb[0]);
    sovellus_kahva = xTaskCreateStatic(sovellus, "sovellus", 256, NULL, 2,
                                       pinot[1], &tcb[1]);
    vTaskStartScheduler();
}
// @loppu main
