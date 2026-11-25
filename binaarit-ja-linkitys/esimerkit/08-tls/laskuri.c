// Säiekohtainen laskuri: jokaisella säikeellä on oma kopionsa.
#include "laskuri.h"

// @alku laskuri
_Thread_local int kutsuja = 0;       // .tbss: nollalla alustettu
_Thread_local int askel = 1;         // .tdata: alkuarvo kopioidaan

int kasvata(void) {
    kutsuja += askel;
    return kutsuja;
}
// @loppu laskuri
