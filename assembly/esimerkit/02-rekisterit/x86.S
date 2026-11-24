    .text
# @alku lisaa32
# long lisaa32(long a, long b): 32-bittinen yhteenlasku.
    .globl lisaa32
lisaa32:
    lea (%rdi,%rsi), %eax       # 32-bittinen kohde nollaa ylimmät bitit
    ret
# @loppu lisaa32

# @alku tavu
# unsigned tavu(const uint32_t *p, long i): sanan tavu i.
    .globl tavu
tavu:
    movzbl (%rdi,%rsi), %eax    # lue tavu, laajenna nollilla
    ret
# @loppu tavu
    .section .note.GNU-stack,"",@progbits
