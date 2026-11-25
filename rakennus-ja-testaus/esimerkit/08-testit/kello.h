// Kellonaika eristetty omaksi rajapinnakseen, jotta testit voivat
// korvata sen linkitysvaiheessa.
#ifndef KELLO_H
#define KELLO_H

#include <time.h>

time_t kello_nyt(void);

#endif
