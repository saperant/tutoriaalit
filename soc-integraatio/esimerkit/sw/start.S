# Käynnistyskoodi ja ansan sisääntulo.
#
# _start: pino-osoitin, ansavektori, .bss nollaksi, main() ja lopetus.
# _ansa:  tallentaa kutsujan tallentamat rekisterit, kutsuu C-funktion
#         ansa(mcause, mepc, mtval), joka palauttaa paluuosoitteen.

    .section .alku, "ax"
    .globl _start
# @alku start
_start:
    la      sp, _pino_loppu
    la      t0, _ansa
    csrw    mtvec, t0           # suora tila: kaikki ansat osoitteeseen
    la      t0, _bss_alku
    la      t1, _bss_loppu
1:  bgeu    t0, t1, 2f          # C olettaa nollatun .bss-osion
    sw      zero, 0(t0)
    addi    t0, t0, 4
    j       1b
2:  call    main
    call    lopeta              # paluukoodi on jo a0:ssa
3:  j       3b
# @loppu start

    .text
    .balign 4
# @alku ansa
_ansa:
    addi    sp, sp, -64
    sw      ra,  0(sp)
    sw      t0,  4(sp)
    sw      t1,  8(sp)
    sw      t2, 12(sp)
    sw      a0, 16(sp)
    sw      a1, 20(sp)
    sw      a2, 24(sp)
    sw      a3, 28(sp)
    sw      a4, 32(sp)
    sw      a5, 36(sp)
    sw      a6, 40(sp)
    sw      a7, 44(sp)
    sw      t3, 48(sp)
    sw      t4, 52(sp)
    sw      t5, 56(sp)
    sw      t6, 60(sp)
    csrr    a0, mcause
    csrr    a1, mepc
    csrr    a2, mtval
    call    ansa                # palauttaa uuden mepc:n
    csrw    mepc, a0
    lw      ra,  0(sp)
    lw      t0,  4(sp)
    lw      t1,  8(sp)
    lw      t2, 12(sp)
    lw      a0, 16(sp)
    lw      a1, 20(sp)
    lw      a2, 24(sp)
    lw      a3, 28(sp)
    lw      a4, 32(sp)
    lw      a5, 36(sp)
    lw      a6, 40(sp)
    lw      a7, 44(sp)
    lw      t3, 48(sp)
    lw      t4, 52(sp)
    lw      t5, 56(sp)
    lw      t6, 60(sp)
    addi    sp, sp, 64
    mret
# @loppu ansa
