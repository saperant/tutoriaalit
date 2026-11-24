# Koodin sekaan kirjoitettu tavu sekoittaa lineaarisen purun.
        .intel_syntax noprefix
        .text
        .globl  tarkista
        .type   tarkista, @function
# @alku sekaannus
# int tarkista(int koodi): 1, jos koodi on 42, muuten 0.
tarkista:
        xor     eax, eax
        cmp     edi, 42
        jne     .Lpaluu
        jmp     .Losuma
        .byte   0xe8            # ei käsky: call-käskyn ensimmäinen tavu
.Losuma:
        mov     eax, 1
.Lpaluu:
        ret
# @loppu sekaannus
        .size   tarkista, .-tarkista
        .section .note.GNU-stack, "", @progbits
