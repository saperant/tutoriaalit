/* Vieraan käynnistyskoodi: Multiboot-otsake, pino ja hyppy C:hen.
 * QEMU lataa ohjelman suoraan valitsimella -kernel, joten vieras
 * käynnistyy 32-bittisessä suojatussa tilassa ilman käynnistyslataajaa.
 */
        .section .multiboot, "a"
        .align 4
        .long 0x1BADB002                /* Multiboot-tunniste */
        .long 0x0                       /* liput */
        .long -(0x1BADB002)             /* tarkistussumma */

        .text
        .globl _start
_start:
        mov     $pino_loppu, %esp
        call    vieras_main
1:      hlt
        jmp     1b

        .bss
        .align 16
pino:   .skip   8192
pino_loppu:

        .section .note.GNU-stack, "", @progbits
