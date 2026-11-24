/* Ytimen sisäiset funktiot: tehtava.c tarjoaa nämä jonoille,
 * tapahtumaryhmille ja portille. Sovellus ei käytä näitä. */
#ifndef KIDE_SISAINEN_H
#define KIDE_SISAINEN_H

#include "kide.h"

/* Ajossa oleva tehtävä. PendSV lukee ja kirjoittaa tätä. */
extern TaskHandle_t volatile kide_nykyinen;

// @alku sisaiset
/* Tikin käsittely; palauttaa pdTRUE, jos tehtävää pitää vaihtaa. */
BaseType_t kide_tikki(void);
/* Valitsee seuraavan ajettavan tehtävän (kutsutaan PendSV:stä). */
void kide_valitse_seuraava(void);
/* Siirtää nykyisen tehtävän odottamaan listaan enintään aikarajan
 * ajaksi ja pyytää vaihtoa. Kutsuttava kriittisestä osiosta;
 * vaihto tapahtuu, kun osio päättyy. */
void kide_odota(lista_t *odotuslista, TickType_t aikaraja);
/* Herättää listan tärkeimmän odottajan. Palauttaa pdTRUE, jos
 * herätetty on nykyistä tehtävää tärkeämpi. */
BaseType_t kide_heraa(lista_t *odotuslista);
/* Herättää tietyn tehtävän (tapahtumaryhmät, ilmoitukset). */
BaseType_t kide_heraa_tehtava(TaskHandle_t tehtava);
/* Prioriteetin periytys: haltija saa odottajan prioriteetin. */
void kide_peri_prioriteetti(TaskHandle_t haltija);
/* Palauttaa perusprioriteetin; pdTRUE, jos vaihto tarvitaan. */
BaseType_t kide_palauta_prioriteetti(TaskHandle_t haltija);
// @loppu sisaiset

/* Portti asettaa tämän tehtäväfunktion paluuosoitteeksi. */
void kide_tehtava_palasi(void);

#endif
