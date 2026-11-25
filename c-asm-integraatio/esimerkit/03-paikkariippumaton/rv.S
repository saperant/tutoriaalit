#include "../02-rajapinta/funktio.h"
    .text
# @alku funktio
# long lisaa_ja_tuplaa(long maara): a0 = maara.
FUNKTIO(lisaa_ja_tuplaa)
#ifdef ABSOLUUTTINEN
    lui t0, %hi(laskuri)        # absoluuttinen osoite: ei kelpaa PIE:hen
    addi t0, t0, %lo(laskuri)
#else
    lla t0, laskuri             # osoite suhteessa käskyosoittimeen
#endif
    ld t1, 0(t0)
    add t1, t1, a0
    sd t1, 0(t0)
    mv a0, t1
    tail tuplaa                 # häntäkutsu; linkkeri valitsee reitin
LOPPU(lisaa_ja_tuplaa)
# @loppu funktio
PINO_EI_SUORITETTAVA
