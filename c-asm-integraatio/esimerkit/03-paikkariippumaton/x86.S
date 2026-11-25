#include "../02-rajapinta/funktio.h"
    .text
# @alku funktio
# long lisaa_ja_tuplaa(long maara): rdi = maara.
FUNKTIO(lisaa_ja_tuplaa)
#ifdef ABSOLUUTTINEN
    add %rdi, laskuri           # absoluuttinen osoite: ei kelpaa PIE:hen
    mov laskuri, %rdi
#else
    add %rdi, laskuri(%rip)     # osoite suhteessa käskyosoittimeen
    mov laskuri(%rip), %rdi
#endif
    jmp tuplaa@PLT              # häntäkutsu linkitystaulun kautta
LOPPU(lisaa_ja_tuplaa)
# @loppu funktio
PINO_EI_SUORITETTAVA
