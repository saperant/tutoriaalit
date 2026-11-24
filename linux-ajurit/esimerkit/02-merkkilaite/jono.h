/* Viestijonoajurin ioctl-rajapinta: sama otsake ytimelle ja
 * käyttäjätilan ohjelmille. */
#ifndef JONO_H
#define JONO_H

#include <linux/ioctl.h>
#include <linux/types.h>

/* @alku ioctl */
struct jono_tila {
    __u32 koko;     /* jonon tilavuus tavuina */
    __u32 kaytetty; /* jonossa odottavat tavut */
};

#define JONO_MAGIA 'j'
#define JONO_TILA      _IOR(JONO_MAGIA, 1, struct jono_tila)
#define JONO_TYHJENNA  _IO(JONO_MAGIA, 2)
/* @loppu ioctl */

#endif
