# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

1. **Lue ennen kuin kirjoitat.** Useimmiten assembly-taito tarkoittaa
   kääntäjän tuottaman koodin lukemista. Katso `gcc -S`:n tai Compiler
   Explorerin tulos ennen kuin kirjoitat mitään käsin.
2. **C-viite ja testit ensin.** Jokaiselle assembly-funktiolle selvä
   C-toteutus, tunnetut testivektorit ja rajatapaukset.
3. **ABI on sopimus.** Argumentit, paluuarvot, kutsun yli säilyvät
   rekisterit, pinon tasaus ja paluuarvojen laajennus. Rikkomus näkyy
   usein vasta kaukana virheestä.
4. **Etumerkillinen vai etumerkitön.** Konekielessä tyyppiä ei ole.
   Valitse vertailu- ja laajennuskäsky tietoisesti.
5. **Kommentoi tarkoitus.** `# t[j - 1] <= x: paikka löytyi`, ei
   `# hyppää jos pienempi`.
6. **Pidä rajapinta yksinkertaisena.** Kokonaisluvut ja osoittimet.
   Lukitse tietueiden asettelu `_Static_assert`-tarkistuksilla.
7. **Mittaa.** Käsin kirjoitettu assembly on perusteltua vain, jos se
   on mitatusti nopeampi tai tekee jotain, mitä C ei voi ilmaista.

## Mallit ja niiden tunnistaminen

| Malli | x86-64 | RISC-V |
|-------|--------|--------|
| Nollaus | `xor %eax, %eax` | `li a0, 0` |
| Onko nolla? | `test %rax, %rax` + `je` | `beqz` |
| Kerto vakiolla | `lea (%rdi,%rdi,2), %rax` | `slli` + `add` |
| Välitarkistus | `sub $a` + `cmp` + `ja` | `addi` + `bgtu` |
| Tietueen kenttä | `8(%rdi)` | `8(a0)` |
| Taulukon alkio | `(%rdi,%rsi,8)` | `slli` + `add` + `ld` |
| Hyppytaulu | `jmp *%rax` + `.rodata` | `jr` + `.rodata` |
| Silmukka | taaksepäin hyppäävä `jne` | taaksepäin hyppäävä `bne` |
| Kehys | `push %rbx` … `pop %rbx` | `addi sp, sp, -16`, `sd`/`ld` |
| Järjestelmäkutsu | `syscall` | `ecall` |

## Pikaopas

Paketin pikaopas (`assembly-pikaopas.pdf`) kokoaa rekisterit,
kutsukonventiot, yleisimmät käskyt ja ehdolliset hypyt kahdelle
sivulle.

## Jatkotaidot

- **Tietokonearkkitehtuuri**: miten suoritin käskyt toteuttaa:
  liukuhihna, välimuistit ja ennustus.
- **Objektitiedostot, linkitys ja ABI**: symbolit, relokaatiot,
  `.eh_frame` ja ohjelman lataus.
- **C ja assembly yhteen**: inline-assembly, kääntäjän sisäiset
  funktiot ja SIMD C:stä.
- **Takaisinmallinnus**: ohjelmien analyysi konekielestä ilman
  lähdekoodia.
- **Kääntäjätekniikka**: koodingenerointi RISC-V:lle ja rekisterien
  varaus.

## Lähteet

Ensisijaiset lähteet ovat käskykantojen ja ABI:en määrittelyt:

- *RISC-V Instruction Set Manual*, osat I (käyttäjätila) ja II
  (etuoikeutettu taso). RISC-V International.
  <https://riscv.org/specifications/> (CC BY 4.0).
- *RISC-V ABIs Specification* (psABI, kutsukonventio ja ELF).
  <https://github.com/riscv-non-isa/riscv-elf-psabi-doc> (CC BY 4.0).
- *RISC-V "V" Vector Extension*, versio 1.0.
  <https://github.com/riscvarchive/riscv-v-spec>.
- *Intel 64 and IA-32 Architectures Software Developer's Manual*,
  osa 2 (käskyt). <https://www.intel.com/sdm>.
- *AMD64 Architecture Programmer's Manual*.
  <https://www.amd.com/en/developer/resources/developer-guides-manuals.html>.
- *System V Application Binary Interface, AMD64 Architecture Processor
  Supplement*. <https://gitlab.com/x86-psABIs/x86-64-ABI>.
- *Using as* (GNU-kokoajan käsikirja).
  <https://sourceware.org/binutils/docs/as/>.
- Linuxin järjestelmäkutsujen numerot: `man 2 syscall` ja
  `/usr/include/asm-generic/unistd.h`.
- RFC 1950: *ZLIB Compressed Data Format Specification* (Adler-32).

Oppikirjoja ja verkkoaineistoja:

- Patterson, D. ja Hennessy, J.: *Computer Organization and Design,
  RISC-V Edition*. Morgan Kaufmann.
- Bryant, R. ja O'Hallaron, D.: *Computer Systems: A Programmer's
  Perspective*, luku 3 (x86-64-konekieli).
- Agner Fog: *Optimizing subroutines in assembly language* ja
  käskytaulukot. <https://www.agner.org/optimize/>.
- Compiler Explorer. <https://godbolt.org/>.

Tämä tutoriaali on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
-lisenssillä (CC BY-SA 4.0). Esimerkkikoodit ovat saman lisenssin
alaisia.
