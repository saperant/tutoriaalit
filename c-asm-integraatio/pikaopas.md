---
title: C ja assembly yhteen
subtitle: Pikaopas · GCC · x86-64 ja RISC-V · Linux
---

# Kolme tapaa

| Tapa | Milloin | Optimoija näkee |
|------|---------|-----------------|
| Sisäinen funktio (`__builtin_*`, `_mm_*`, `__riscv_*`) | SIMD, bittioperaatiot | kaiken |
| Inline-assembly (`__asm__`) | yksittäinen käsky ilman C-vastinetta | vain rajoitteet |
| `.S`-tiedosto | kokonaiset funktiot, `_start`, kontekstinvaihto | vain prototyypin |

Ensin C ja `gcc -O2 -S`, sitten sisäiset funktiot, viimeisenä assembly.

# Assembly-tiedoston kehys

Iso `.S` ajetaan esikääntäjän läpi (`__ASSEMBLER__` määritelty),
pieni `.s` ei. Yhteinen otsake C:lle ja assemblylle:

```{.c tiedosto="esimerkit/01-rajapinta/funktio.h" osa="makrot"}
```

Funktio, joka tallentaa rekisterin, CFI:n kanssa:

```{.gnuassembler tiedosto="esimerkit/04-pinonpurku/x86.S" osa="kutsu"}
```

| Direktiivi | Merkitys |
|------------|----------|
| `.globl f` / `.hidden f` | näkyy linkkerille / ei jaetun kirjaston ulkopuolelle |
| `.type f, @function`, `.size f, . - f` | tyyppi ja koko symbolitauluun |
| `.cfi_startproc`, `.cfi_endproc` | purkutiedot alkavat / loppuvat |
| `.cfi_def_cfa_offset n` | CFA = `sp + n` |
| `.cfi_offset rek, n` | rekisteri tallessa osoitteessa CFA + n |
| `.section .note.GNU-stack,"",@progbits` | pino ei suoritettava |

# Kutsusopimus rajapintana

| Lupaus | x86-64 (System V) | RISC-V (psABI) |
|--------|-------------------|----------------|
| Säilyvät rekisterit | `rbx rbp r12–r15` | `s0`–`s11` |
| Pino ennen `call` | `rsp` 16:lla jaollinen | `sp` aina 16:lla jaollinen |
| Alle 64 b argumentti | yläbitit määrittelemättömät | laajennettu tyypin mukaan |
| `char` | etumerkillinen | etumerkitön |
| Epäsuoran kutsun kohde (CET) | `endbr64` (`_CET_ENDBR`) | – |

# Inline-assembly

```text
__asm__ [volatile] ("pohja %[x], %1"
    : [x] "+r"(x), "=&r"(apu)      // tulosteet
    : "r"(y), "i"(VAKIO), "m"(*p)  // syötteet
    : "t0", "cc", "memory");       // sotkettavat
```

| Rajoite | Merkitys | Huomio |
|---------|----------|--------|
| `r`, `m`, `i` | rekisteri, muisti, vakio | `i` tuottaa x86:lla `$`-merkin |
| `=` / `+` | pelkkä tuloste / syöte ja tuloste | |
| `&` | tuloste kirjoitetaan ennen syötteiden lukua | puuttuminen → sama rekisteri |
| `0`, `1`, … | sama paikka kuin operandi n | |
| `a b c d S D` | x86: `rax rbx rcx rdx rsi rdi` | `cpuid`, `mul`, `rdtsc` |
| `I`, `f` | RISC-V: 12 b vakio, liukulukurekisteri | |
| `"memory"` | luetaan / kirjoitetaan muuta muistia | kääntäjän muistieste |
| `volatile` | ei saa poistaa eikä yhdistää | ajastimet, `cpuid`, esteet |

Virheet näkyvät vasta optimoidessa: puuttuva `"memory"` → vanha arvo,
puuttuva `&` → syöte ylikirjoittuu, puuttuva `volatile` → lause
poistuu. Testaa `-O2`:lla ja `-O3`:lla.

```{.c tiedosto="esimerkit/05-inline/main.c" osa="muisti"}
```

# Sisäiset funktiot

| Funktio | x86-64 | RISC-V |
|---------|--------|--------|
| `__builtin_popcountll` | `popcnt` (`-mpopcnt`), muuten kutsu | `cpop` (Zbb), muuten kutsu |
| `__builtin_ctzll`, `__builtin_clzll` | `tzcnt`/`bsf`, `lzcnt`/`bsr` | `ctz`, `clz` (Zbb) |
| `__builtin_bswap64` | `bswap` | `rev8` (Zbb), muuten kutsu |
| `__builtin_add_overflow` | `add` + `jo` | `add` + vertailu |
| `__builtin_expect(e, 0)` | harvinainen haara sivuun | sama |

Intelin nimet: `_mm_` 128 b, `_mm256_` 256 b; `epi8` … `epi64`
etumerkilliset, `epu8` etumerkittömät, `ps`/`pd` float/double,
`si128` koko rekisteri. RISC-V: `__riscv_vle8_v_u8m1` = lataus,
8 b etumerkitön, LMUL 1; `__riscv_vsetvl_e8m1(n)` antaa kierroksen
pituuden.

```{.c tiedosto="esimerkit/08-simd/simd.c" osa="rvv"}
```

# Ajonaikainen valinta

| Asia | x86-64 | RISC-V Linux |
|------|--------|--------------|
| Tunnistus | `__builtin_cpu_supports("avx2")`, `cpuid` + `xgetbv` | `getauxval(AT_HWCAP)`, `__riscv_hwprobe` |
| Yksi funktio laajennukselle | `__attribute__((target("avx2")))` | erillinen tiedosto `-march=rv64gcv` |
| Automaattiset versiot | `target_clones("avx2", "default")` | ei GCC 13:ssa |
| Testaus | `qemu-x86_64 -cpu Nehalem` / `Haswell-noTSX` | `QEMU_CPU=rv64,v=true` |

```{.c tiedosto="esimerkit/09-ominaisuudet/laske.c" osa="ifunc"}
```

# Tarkistukset

| Tarkoitus | Komento |
|-----------|---------|
| Symbolin tyyppi ja koko | `readelf -sW f.o` |
| Pinon oikeudet | `readelf -lW ohjelma` (`GNU_STACK RW`, ei `RWE`) |
| Purkutiedot | `readelf --debug-dump=frames f.o` |
| Funktion käskyt | `objdump -d --disassemble=f ohjelma` |
| Vektoroinnin syy | `gcc -O3 -fopt-info-vec-missed` |
| Rekisterien noudatus | rekisterivahti: täytä säilyvät, kutsu, vertaa |
