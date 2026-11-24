/* Aikajana: mikä tehtävä ajoi minkäkin tikin aikana. Tikkikoukku
 * kirjaa jokaisen tikin välin sille tehtävälle, jonka aikana tikki-
 * keskeytys tuli, eli samalle, jolle ydin kirjaa ajoajan. */
#ifndef AIKAJANA_H
#define AIKAJANA_H

#include "kide.h"

#define AIKAJANA_TIKIT 72u   /* mahtuu PDF:n riville */

/* Lisää tehtävän aikajanan riveille (enintään 8, lisäysjärjestys). */
void aikajana_lisaa(TaskHandle_t tehtava);
/* Tulostaa välin [0, loppu) tikit. */
void aikajana_tulosta(TickType_t loppu);
/* Tulostaa rivien tehtävien prioriteetin, ajoajan ja valintakerrat. */
void aikajana_tilastot(void);

#endif
