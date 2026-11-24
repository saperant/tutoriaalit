/* Porttikerros: kaikki, mikä riippuu prosessorista.
 *
 * Ytimen loppuosa (tehtava.c, jono.c, tapahtumat.c, muisti.c) on
 * tavallista C:tä. Portti toteuttaa pinon alustuksen, ensimmäisen
 * tehtävän käynnistyksen, tehtävänvaihdon ja kriittiset osiot.
 * Cortex-M3:n portti on tiedostossa portti_cm3.c ja isäntäkoneen
 * (Linux, ucontext) portti tiedostossa ../isanta/portti_isanta.c. */
#ifndef PORTTI_H
#define PORTTI_H

#include <stdint.h>

#ifdef KIDE_ISANTA
#include <ucontext.h>
/* Isäntäportti tallentaa tehtävän tilan ucontext-rakenteeseen. */
#define PORTTI_TCB_KENTAT ucontext_t konteksti;
#else
#define PORTTI_TCB_KENTAT
#endif

typedef uint32_t StackType_t;
typedef void (*TaskFunction_t)(void *);
struct tcb;

// @alku rajapinta
/* Rakentaa uuden tehtävän pinoon kehyksen, josta tehtävä käynnistyy
 * kuin se palaisi keskeytyksestä. Palauttaa pino-osoittimen. */
StackType_t *portti_alusta_pino(struct tcb *tcb, StackType_t *huippu);
/* Käynnistää tikkiajastimen ja ensimmäisen tehtävän; ei palaa. */
_Noreturn void portti_kaynnista(void);
/* Pyytää tehtävänvaihtoa. Kriittisessä osiossa vaihto tapahtuu
 * vasta, kun osio päättyy. */
void portti_vaihda(void);
/* Kriittinen osio tehtävästä: sisäkkäiset kutsut sallittu. */
void portti_kriittinen_alku(void);
void portti_kriittinen_loppu(void);
/* Kriittinen osio keskeytyskäsittelijästä: palauttaa vanhan tilan. */
uint32_t portti_peita_isr(void);
void portti_palauta_isr(uint32_t vanha);
/* Varmistaa, että FromISR-funktiota kutsutaan sallitulta
 * keskeytysprioriteetilta. */
void portti_tarkista_isr(void);
/* Kuluttaa prosessoriaikaa, kunnes tehtävä on ajanut annetun
 * määrän tikkejä (simuloitu laskentatyö). */
void portti_kuormita(uint32_t tikit);
/* Idle-tehtävän odotus: Cortex-M:ssä WFI. */
void portti_odota(void);
// @loppu rajapinta

#endif
