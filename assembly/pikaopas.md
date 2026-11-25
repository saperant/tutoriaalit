---
title: Assembly
subtitle: Pikaopas · x86-64 (AT&T) ja RISC-V (RV64GC) · Linux
---

# Työkalut

| Tarkoitus | x86-64 | RISC-V |
|-----------|--------|--------|
| Kokoa ja linkitä | `gcc -c f.S`, `gcc main.c f.S` | `riscv64-linux-gnu-gcc -static main.c f.S` |
| Ilman libc:tä | `gcc -nostdlib -static f.S` | `riscv64-linux-gnu-gcc -nostdlib -static f.S` |
| Kääntäjän tuottama koodi | `gcc -O2 -S f.c` | `riscv64-linux-gnu-gcc -O2 -S f.c` |
| Puretut käskyt | `objdump -d f.o` | `riscv64-linux-gnu-objdump -d f.o` |
| Ajo | natiivisti | `qemu-riscv64 ./ohjelma` |
| Debuggaus | `gdb`: `stepi`, `info registers`, `x/16xb $rsp` | `qemu-riscv64 -g 1234` + `gdb-multiarch` |
| Järjestelmäkutsut | `strace ./ohjelma` | `qemu-riscv64 -strace ./ohjelma` |

Intel-syntaksi: `objdump -M intel`, `gcc -masm=intel`. Vektorit
QEMU:ssa: `QEMU_CPU=rv64,v=true,vlen=128,vext_spec=v1.0`.

# Kutsukonventiot

| Asia | System V AMD64 | RISC-V psABI (LP64D) |
|----------------------|-----------------------------|----------------------------|
| Kokonaislukuargumentit | `rdi rsi rdx rcx r8 r9` | `a0`–`a7` |
| Liukulukuargumentit | `xmm0`–`xmm7` | `fa0`–`fa7` |
| Paluuarvo | `rax` (`rdx`), `xmm0` | `a0` (`a1`), `fa0` |
| Kutsun yli säilyvät | `rbx rbp r12–r15 rsp` | `s0`–`s11`, `sp`, `fs0`–`fs11` |
| Kutsujan tallennettavat | muut | `t0`–`t6`, `a0`–`a7`, `ra` |
| Paluuosoite | pinossa (`call` / `ret`) | `ra` (`call` / `ret`) |
| Pinon tasaus | 16 tavua ennen `call`-käskyä | 16 tavua aina |
| 32-bittinen paluuarvo | ylimmät bitit määrittelemättömät | etumerkillä laajennettu (`sext.w`) |
| Punainen alue | 128 tavua `rsp`:n alla | ei ole |

Lehtifunktio, joka käyttää vain kutsujan tallennettavia rekistereitä,
ei tarvitse kehystä. Muuten tallenna säilytettävät rekisterit ja
pidä pino tasattuna:

```{.gnuassembler tiedosto="esimerkit/05-pino/x86.S" osa="kertoma"}
```

```{.gnuassembler tiedosto="esimerkit/05-pino/rv.S" osa="kertoma"}
```

# Rekisterit

| x86-64 | 32 / 16 / 8 b | Rooli | RISC-V | ABI-nimi | Rooli |
|--------|---------------|-------|--------|----------|-------|
| `rax` | `eax ax al` | paluuarvo | `x0` | `zero` | aina 0 |
| `rdi`, `rsi` | `edi`, `esi` | arg. 1–2 | `x1` | `ra` | paluuosoite |
| `rdx`, `rcx` | `edx`, `ecx` | arg. 3–4 | `x2` | `sp` | pino |
| `r8`, `r9` | `r8d`, `r9d` | arg. 5–6 | `x5–7`, `x28–31` | `t0`–`t6` | väliaikaiset |
| `rbx`, `rbp` | `ebx`, `ebp` | säilyvät | `x8–9`, `x18–27` | `s0`–`s11` | säilyvät |
| `r12`–`r15` | `r12d` … | säilyvät | `x10–17` | `a0`–`a7` | argumentit |
| `rsp` | `esp` | pino | `pc` | – | ei suoraan |

x86-64: kirjoitus 32-bittiseen rekisteriin nollaa ylimmät 32 bittiä,
8- ja 16-bittiseen ei.

# Yleisimmät käskyt

| Tehtävä | x86-64 (AT&T: lähde, kohde) | RISC-V |
|----------------|------------------------------------------|-------------------------------|
| Kopioi | `mov %rsi, %rax` | `mv a0, a1` |
| Vakio | `mov $42, %eax` | `li a0, 42` |
| Osoite | `lea sym(%rip), %rax` | `la a0, sym` |
| Lataa 64 / 32 b | `mov 8(%rdi), %rax`, `mov (%rdi), %eax` | `ld a0, 8(a0)`, `lw` / `lwu` |
| Lataa tavu | `movzbl` / `movsbl (%rdi), %eax` | `lbu` / `lb a0, 0(a0)` |
| Tallenna | `mov %rax, 8(%rdi)` | `sd a1, 8(a0)` |
| Indeksi | `(%rdi,%rsi,8)` | `slli t0, a1, 3` + `add` + `ld` |
| Laske | `add %rsi, %rax`, `sub`, `imul` | `add a0, a0, a1`, `sub`, `mul` |
| 32-bittinen | `addl`, `%eax` | `addw`, `subw`, `mulw` |
| Jako | `cqo` + `idiv %rcx` / `xor %edx,%edx` + `div` | `div`, `rem`, `divu`, `remu` |
| Bitit | `and or xor not` | `and or xor`, `not` |
| Siirrot | `shl sar shr $n, %rax` | `slli srai srli a0, a0, n` |
| Kerto vakiolla | `lea (%rdi,%rdi,4), %rax` | `slli` + `add` |
| Etumerkki 32 → 64 | `movslq %edi, %rax` | `sext.w a0, a0` |
| Nollaa | `xor %eax, %eax` | `li a0, 0` |
| Pino | `push`, `pop`, `sub $16, %rsp` | `addi sp, sp, -16`, `sd ra, 8(sp)` |
| Kutsu, paluu | `call f`, `ret`, `call *%rax` | `call f`, `ret`, `jalr a5` |
| Järjestelmäkutsu | `syscall` (`rax` = nro, `r10` = arg. 4) | `ecall` (`a7` = nro) |

# Vertailu ja hypyt

| Ehto | x86-64: `cmp %rsi, %rdi` + | RISC-V |
|----------------------|------------------------------|-----------------------------|
| `a == b` | `je` | `beq a0, a1, L` |
| `a != b` | `jne` | `bne` |
| `a < b` etumerkillinen | `jl` | `blt` |
| `a >= b` etumerkillinen | `jge` | `bge` |
| `a > b`, `a <= b` | `jg`, `jle` | `bgt`, `ble` (vaihdetut `blt`, `bge`) |
| `a < b` etumerkitön | `jb` | `bltu` |
| `a >= b` etumerkitön | `jae` | `bgeu` |
| `a > b`, `a <= b` etumerkitön | `ja`, `jbe` | `bgtu`, `bleu` |
| `a == 0` | `test %rdi, %rdi` + `je` | `beqz a0, L` |
| Ehto arvoksi | `setl %al` + `movzbl` | `slt a0, a0, a1`, `sltu`, `seqz`, `snez` |
| Ehdollinen siirto | `cmovl %rsi, %rax` | haara tai `czero` (Zicond) |
| Ylivuoto | `jo`, `seto` (etumerkillinen), `jc`, `setc` | `sltu` summasta, xor-tarkistus |

Välitarkistus `lo ≤ x ≤ hi` yhdellä etumerkittömällä vertailulla:
`x - lo ≤ hi - lo`.

# Järjestelmäkutsut (Linux)

| Kutsu | x86-64 | RISC-V | Argumentit |
|-------|--------|--------|------------|
| `read` | 0 | 63 | tiedosto, puskuri, koko |
| `write` | 1 | 64 | tiedosto, puskuri, koko |
| `openat` | 257 | 56 | hakemisto, polku, liput, oikeudet |
| `close` | 3 | 57 | tiedosto |
| `mmap` | 9 | 222 | osoite, koko, suojaus, liput, fd, siirtymä |
| `exit` | 60 | 93 | koodi |
| `exit_group` | 231 | 94 | koodi |

Paluuarvo −4095…−1 on `-errno`. x86-64:llä `syscall` tuhoaa `rcx`:n ja
`r11`:n.

# Kokoajan direktiivit

| Direktiivi | Merkitys |
|------------|----------|
| `.text`, `.data`, `.rodata`, `.bss` | osio (`.section .rodata`) |
| `.globl f` | symboli näkyy linkittäjälle |
| `.byte .short .long .quad` | 1 / 2 / 4 / 8 tavun data (`.word` = 4 RISC-V:llä) |
| `.ascii "..."`, `.asciz "..."` | merkkijono ilman / nollatavun kanssa |
| `.space n`, `.balign 16` | varaa tavuja, tasaa |
| `.set nimi, arvo`, `. - alku` | vakio, nykyinen osoite |
| `1:` … `jmp 1b` / `1f` | paikalliset nimiöt taakse / eteen |
| `.option arch, +v` | ota RISC-V-laajennus käyttöön tiedostossa |
| `.section .note.GNU-stack,"",@progbits` | pino ei suoritettava |

# SIMD lyhyesti

| Asia | SSE2 / AVX2 | RISC-V V |
|-------------------|------------------------------|------------------------------|
| Rekisterit | `xmm0–15` (128 b), `ymm0–15` (256 b) | `v0`–`v31`, VLEN toteutuskohtainen |
| Pituuden valinta | kiinteä, häntä erikseen | `vsetvli t0, a1, e32, m1, tu, ma` |
| Lataus | `movdqu`, `vmovdqu` | `vle32.v v8, (a0)` |
| Kokonaislukusumma | `paddd`, `vpaddd` | `vadd.vv` |
| Kaistojen summa | `pshufd` + `paddd` kahdesti | `vredsum.vs` |
| Tuen tarkistus | `__builtin_cpu_supports("avx2")` | `hwprobe` / `/proc/cpuinfo` |
| Lopetus | `vzeroupper` ennen SSE-koodia | – |
