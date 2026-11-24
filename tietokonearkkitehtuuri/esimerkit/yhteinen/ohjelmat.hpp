// Testiohjelmat RV32I-assemblynä. Jokainen tulostaa tuloksensa
// järjestelmäkutsulla ja päättyy kutsuun a7 = 10.
#pragma once
#include <string_view>

namespace ohjelmat {

// @alku summa
// Täyttää taulukon a[i] = 3i + 1 (i < 200) ja laskee summan.
inline constexpr std::string_view summa = R"(
        la   s0, taulukko
        li   s1, 200
        li   t0, 0
alusta: slli t1, t0, 1
        add  t1, t1, t0          # 3i
        addi t1, t1, 1
        slli t2, t0, 2
        add  t2, s0, t2
        sw   t1, 0(t2)
        addi t0, t0, 1
        blt  t0, s1, alusta
        li   a0, 0
        li   t0, 0
summaa: slli t2, t0, 2
        add  t2, s0, t2
        lw   t1, 0(t2)
        add  a0, a0, t1          # käyttää heti ladattua arvoa
        addi t0, t0, 1
        blt  t0, s1, summaa
        li   a7, 1
        ecall
        li   a7, 10
        ecall
taulukko:
        .zero 800
)";
// @loppu summa

// @alku kupla
// Kuplalajittelu 48 alkiolle, joiden arvot tulevat lineaarisesta
// kongruenssigeneraattorista. Tulostaa pienimmän ja suurimman.
inline constexpr std::string_view kupla = R"(
        la   s0, taulukko
        li   s1, 48
        li   t0, 0
        li   t3, 12345
alusta: li   t4, 1103
        mul  t3, t3, t4
        addi t3, t3, 1013
        andi t1, t3, 1023
        slli t2, t0, 2
        add  t2, s0, t2
        sw   t1, 0(t2)
        addi t0, t0, 1
        blt  t0, s1, alusta
        addi s2, s1, -1          # ulompi: n-1 kierrosta
ulompi: li   t0, 0
sisempi:
        slli t2, t0, 2
        add  t2, s0, t2
        lw   t4, 0(t2)
        lw   t5, 4(t2)
        ble  t4, t5, ohi         # vaihdetaan vain väärässä järjestyksessä
        sw   t5, 0(t2)
        sw   t4, 4(t2)
ohi:    addi t0, t0, 1
        blt  t0, s2, sisempi
        addi s2, s2, -1
        bnez s2, ulompi
        lw   a0, 0(s0)
        li   a7, 1
        ecall
        li   a0, 32
        li   a7, 11
        ecall
        lw   a0, 188(s0)
        li   a7, 1
        ecall
        li   a7, 10
        ecall
taulukko:
        .zero 192
)";
// @loppu kupla

// @alku matriisi
// C = A B kahdelle 12 x 12 -matriisille, A[i][j] = i + j ja
// B[i][j] = i j + 1. Tulostaa C:n jäljen.
inline constexpr std::string_view matriisi = R"(
        la   s0, A
        la   s1, B
        la   s2, C
        li   s3, 12
        li   t0, 0                # i
tayta_i: li  t1, 0                # j
tayta_j: mul t2, t0, s3
        add  t2, t2, t1
        slli t2, t2, 2           # (i*12 + j) * 4
        add  t3, t0, t1
        add  t4, s0, t2
        sw   t3, 0(t4)
        mul  t3, t0, t1
        addi t3, t3, 1
        add  t4, s1, t2
        sw   t3, 0(t4)
        addi t1, t1, 1
        blt  t1, s3, tayta_j
        addi t0, t0, 1
        blt  t0, s3, tayta_i
        li   t0, 0                # i
rivi:   li   t1, 0                # j
sarake: li   t5, 0                # summa
        li   t2, 0                # k
pistetulo:
        mul  t3, t0, s3
        add  t3, t3, t2
        slli t3, t3, 2
        add  t3, s0, t3
        lw   t3, 0(t3)            # A[i][k]
        mul  t4, t2, s3
        add  t4, t4, t1
        slli t4, t4, 2
        add  t4, s1, t4
        lw   t4, 0(t4)            # B[k][j]
        mul  t3, t3, t4
        add  t5, t5, t3
        addi t2, t2, 1
        blt  t2, s3, pistetulo
        mul  t3, t0, s3
        add  t3, t3, t1
        slli t3, t3, 2
        add  t3, s2, t3
        sw   t5, 0(t3)
        addi t1, t1, 1
        blt  t1, s3, sarake
        addi t0, t0, 1
        blt  t0, s3, rivi
        li   a0, 0                # jälki: C[i][i]:n summa
        li   t0, 0
jalki:  mul  t3, t0, s3
        add  t3, t3, t0
        slli t3, t3, 2
        add  t3, s2, t3
        lw   t3, 0(t3)
        add  a0, a0, t3
        addi t0, t0, 1
        blt  t0, s3, jalki
        li   a7, 1
        ecall
        li   a7, 10
        ecall
A:      .zero 576
B:      .zero 576
C:      .zero 576
)";
// @loppu matriisi

// @alku fib
// Rekursiivinen fib(16): paljon kutsuja, paluita ja pinon käyttöä.
inline constexpr std::string_view fib = R"(
        li   a0, 16
        call fib
        li   a7, 1
        ecall
        li   a7, 10
        ecall
fib:    li   t0, 2
        blt  a0, t0, pieni
        addi sp, sp, -12
        sw   ra, 8(sp)
        sw   s0, 4(sp)
        sw   a0, 0(sp)
        addi a0, a0, -1
        call fib
        mv   s0, a0
        lw   a0, 0(sp)
        addi a0, a0, -2
        call fib
        add  a0, a0, s0
        lw   ra, 8(sp)
        lw   s0, 4(sp)
        addi sp, sp, 12
pieni:  ret
)";
// @loppu fib

// @alku lista
// Linkitetty lista, jonka solmut ovat muistissa sekalaisessa
// järjestyksessä (indeksi i -> 37 i mod 64). Kulkee listan läpi ja
// laskee arvojen summan: jokainen lataus riippuu edellisestä.
inline constexpr std::string_view lista = R"(
        la   s0, solmut
        li   s1, 64
        li   t0, 0
rakenna:
        li   t2, 37
        mul  t1, t0, t2
        andi t1, t1, 63          # nykyinen paikka
        addi t2, t0, 1
        li   t3, 37
        mul  t2, t2, t3
        andi t2, t2, 63          # seuraavan paikka
        slli t1, t1, 3
        add  t1, s0, t1
        slli t2, t2, 3
        add  t2, s0, t2
        addi t4, t0, 1
        sw   t4, 0(t1)           # arvo
        sw   t2, 4(t1)           # osoitin seuraavaan
        addi t0, t0, 1
        blt  t0, s1, rakenna
        li   a0, 0
        mv   t1, s0              # aloitetaan paikasta 0
        li   t0, 0
kulje:  lw   t4, 0(t1)
        add  a0, a0, t4
        lw   t1, 4(t1)           # seuraava riippuu tästä latauksesta
        addi t0, t0, 1
        blt  t0, s1, kulje
        li   a7, 1
        ecall
        li   a7, 10
        ecall
solmut: .zero 512
)";
// @loppu lista

}  // namespace ohjelmat
