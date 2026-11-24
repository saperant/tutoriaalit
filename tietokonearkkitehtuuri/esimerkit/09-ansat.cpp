// Poikkeukset ja keskeytykset: käsittelijä mtvec:ssä, syy mcause:ssa,
// paluuosoite mepc:ssä. Lopuksi tulostus muistiinkuvatulla UARTilla.
#include <format>
#include <print>
#include <string_view>

#include "yhteinen/kone.hpp"

// @alku ohjelma
constexpr std::string_view ohjelma = R"(
        la   t0, kasittelija
        csrw mtvec, t0
        la   s0, loki
        ecall                    # 1: ympäristökutsu
        .word 0                  # 2: laiton käsky (kaikki bitit nollia)
        li   t1, 0x102
        lw   t2, 0(t1)           # 3: kohdistamaton lataus
        li   t1, 0x02004000      # mtimecmp
        li   t2, 100
        sw   t2, 0(t1)           # ajastin laukeaa jaksossa 100
        li   t1, 0x80
        csrw mie, t1             # MTIE: ajastinkeskeytys sallittu
        li   t1, 8
        csrw mstatus, t1         # MIE: keskeytykset päälle
        li   s1, 0
odota:  li   t1, 3
        blt  s1, t1, odota       # odotetaan kolmea keskeytystä
        csrw mstatus, zero
        li   t1, 0x10000000      # UART
        li   t2, 79
        sw   t2, 0(t1)           # 'O'
        li   t2, 75
        sw   t2, 0(t1)           # 'K'
loppu:  j    loppu

kasittelija:
        csrr t5, mcause
        csrr t6, mepc
        sw   t5, 0(s0)           # kirjataan syy ja osoite lokiin
        sw   t6, 4(s0)
        addi s0, s0, 8
        blt  t5, zero, keskeytys # ylin bitti 1 = keskeytys
        addi t6, t6, 4           # poikkeus: ohitetaan aiheuttaja
        csrw mepc, t6
        mret
keskeytys:
        addi s1, s1, 1
        li   t5, 0x02004000
        lw   t6, 0(t5)
        addi t6, t6, 100         # seuraava keskeytys 100 jakson päästä
        sw   t6, 0(t5)
        mret
loki:   .zero 64
)";
// @loppu ohjelma

int main() {
    // @alku ajo
    const rv::Ohjelma o = rv::koota(ohjelma);
    rv::Kone kone(o);
    kone.ansat = true;
    while (kone.pc != o.nimiot.at("loppu")) kone.askel();
    std::println("UART: {}  ({} käskyä)", kone.tuloste, kone.suoritetut);
    const rv::u32 loki = o.nimiot.at("loki");
    for (rv::u32 a = loki; kone.lue(a, 4) != 0; a += 8) {
        const rv::u32 syy = kone.lue(a, 4), mepc = kone.lue(a + 4, 4);
        const bool keskeytys = syy >> 31;
        const char* selitys = keskeytys ? "ajastinkeskeytys"
                              : syy == 2 ? "laiton käsky"
                              : syy == 4 ? "kohdistamaton lataus"
                              : syy == 11 ? "ecall M-tilasta"
                                          : "?";
        const rv::u32 k = kone.lue(mepc, 4);
        std::println("mcause 0x{:08x}  mepc 0x{:03x}  {:<21} {}", syy,
                     mepc, selitys,
                     syy == 2 ? std::format(".word 0x{:08x}", k)
                              : rv::pura_teksti(k, mepc));
    }
    // @loppu ajo
}
