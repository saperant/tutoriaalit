#include <stdio.h>

#include "komento.h"

static int versio(void) { return puts("työkalu 3.1") < 0; }
KOMENTO("versio", versio);
