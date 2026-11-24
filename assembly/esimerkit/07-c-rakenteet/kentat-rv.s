    .text
    .globl    tilauksen_arvo
tilauksen_arvo:
    lw    a5,4(a0)
    fld    fa5,8(a0)
    fcvt.d.w    fa0,a5
    fmul.d    fa0,fa0,fa5
    ret
    .globl    tilauksen_asiakas
tilauksen_asiakas:
    ld    a0,16(a0)
    ret
