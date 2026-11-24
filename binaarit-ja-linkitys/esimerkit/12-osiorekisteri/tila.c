#include <stdio.h>

#include "komento.h"

static int tila(void) { return puts("kaikki kunnossa") < 0; }
KOMENTO("tila", tila);
