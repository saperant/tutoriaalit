# int32_t-taulukon summa skalaarina, SSE2:lla (4 alkiota kerralla) ja
# AVX2:lla (8 alkiota). Vektoriversioissa n on 8:n monikerta.
    .text
# @alku skalaari
    .globl summa_skalaari
summa_skalaari:
    xor %eax, %eax              # summa
    xor %ecx, %ecx              # i
1:  cmp %rsi, %rcx
    jae 2f
    add (%rdi,%rcx,4), %eax
    inc %rcx
    jmp 1b
2:  ret
# @loppu skalaari

# @alku sse2
    .globl summa_sse2
summa_sse2:
    pxor %xmm0, %xmm0           # neljä osasummaa = 0
    xor %eax, %eax              # i
1:  cmp %rsi, %rax
    jae 2f
    movdqu (%rdi,%rax,4), %xmm1 # t[i .. i+3]
    paddd %xmm1, %xmm0          # osasummat += t[i .. i+3]
    add $4, %rax
    jmp 1b
2:  pshufd $0x4e, %xmm0, %xmm1  # vaihda puoliskot: [2 3 0 1]
    paddd %xmm1, %xmm0
    pshufd $0xb1, %xmm0, %xmm1  # vaihda parit: [1 0 3 2]
    paddd %xmm1, %xmm0          # kaikissa kaistoissa sama summa
    movd %xmm0, %eax
    ret
# @loppu sse2

# @alku avx2
    .globl summa_avx2
summa_avx2:
    vpxor %ymm0, %ymm0, %ymm0   # kahdeksan osasummaa = 0
    xor %eax, %eax
1:  cmp %rsi, %rax
    jae 2f
    vpaddd (%rdi,%rax,4), %ymm0, %ymm0
    add $8, %rax
    jmp 1b
2:  vextracti128 $1, %ymm0, %xmm1   # ylempi 128-bittinen puolisko
    vpaddd %xmm1, %xmm0, %xmm0
    vpshufd $0x4e, %xmm0, %xmm1
    vpaddd %xmm1, %xmm0, %xmm0
    vpshufd $0xb1, %xmm0, %xmm1
    vpaddd %xmm1, %xmm0, %xmm0
    vmovd %xmm0, %eax
    vzeroupper                  # ennen paluuta SSE-koodiin
    ret
# @loppu avx2
    .section .note.GNU-stack,"",@progbits
