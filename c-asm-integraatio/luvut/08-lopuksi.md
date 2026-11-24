# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **C ensin, assembly viimeisenä.** Järjestys on C, kääntäjän
   tuottaman koodin lukeminen, vektoroitava C, sisäiset funktiot,
   inline-assembly ja `.S`-tiedosto. Jokainen askel perustellaan
   mittauksella tai sillä, ettei C voi ilmaista asiaa.
2. **Rajapinta on sopimus.** Prototyyppi otsakkeeseen, rekisterit
   kommenttiin, argumentit laajennetaan itse, säilyvät rekisterit
   palautetaan ja pino tasataan. Rekisterivahti testaa sopimuksen.
3. **Metatiedot jokaiseen funktioon.** `.type`, `.size`, CFI ja
   `.note.GNU-stack` makroilla, jotta mikään ei unohdu.
4. **Inline-assemblyssä kerrotaan kaikki.** Tulosteet, syötteet,
   sotkettavat, `"memory"` ja `&`. Kääntäjä uskoo jokaisen sanan.
5. **Testaa optimoiden ja kaikilla poluilla.** `-O2` ja `-O3`, kaikki
   pituudet ja tasaukset, jokainen ajonaikaisen valinnan haara
   emuloidulla prosessorilla.
6. **Pidä C-versio.** Se on viite, varapolku ja mittatikku.

## Pikaopas

Paketin pikaopas (`c-asm-integraatio-pikaopas.pdf`) kokoaa
inline-assemblyn rajoitteet, sotkettavat, tärkeimmät sisäiset
funktiot, assembly-tiedoston kehyksen ja ajonaikaisen tunnistuksen
kahdelle sivulle.

## Jatkotaidot

- **Objektitiedostot, linkitys ja ABI**: relokaatiot, PLT ja GOT,
  `.eh_frame`-osion rakenne ja ohjelman lataus.
- **Tietokonearkkitehtuuri**: miksi jakolasku on hidas, mitä
  vektoriyksiköt tekevät ja miten liukuhihna vaikuttaa käskyjen
  ajoitukseen.
- **Suorituskyvyn mittaaminen**: `perf`, laitteistolaskurit ja
  mikrobenchmarkien sudenkuopat.
- **Takaisinmallinnus**: kääntäjän tuottaman koodin tunnistaminen ilman
  lähdekoodia.
- **Käyttöjärjestelmän ydin**: kontekstinvaihto, keskeytykset ja
  etuoikeutetut käskyt, joissa assemblyä todella tarvitaan.

## Lähteet

GCC:n ja binutilsin käsikirjat ovat ensisijaiset lähteet
inline-assemblylle, sisäisille funktioille ja kokoajan direktiiveille:

- *Using the GNU Compiler Collection*: Extended Asm, Constraints for
  asm Operands, Other Built-in Functions, x86 ja RISC-V Built-in
  Functions sekä Common Function Attributes (`ifunc`, `target`,
  `target_clones`). <https://gcc.gnu.org/onlinedocs/gcc/>.
- *Using as*: CFI-direktiivit, makrot (`.macro`, `.irp`) ja
  symbolidirektiivit. <https://sourceware.org/binutils/docs/as/>.
- *System V Application Binary Interface, AMD64 Architecture Processor
  Supplement*. <https://gitlab.com/x86-psABIs/x86-64-ABI>.
- *RISC-V ABIs Specification* (psABI).
  <https://github.com/riscv-non-isa/riscv-elf-psabi-doc> (CC BY 4.0).
- *Intel Intrinsics Guide*.
  <https://www.intel.com/content/www/us/en/docs/intrinsics-guide/>.
- *RISC-V Vector Extension Intrinsic Document*.
  <https://github.com/riscv-non-isa/rvv-intrinsic-doc> (CC BY 4.0).
- *Intel 64 and IA-32 Architectures Software Developer's Manual*,
  osat 1 (XSAVE ja XCR0) ja 2 (`cpuid`). <https://www.intel.com/sdm>.
- Linuxin RISC-V-dokumentaatio: *RISC-V Hardware Probing Interface*.
  <https://docs.kernel.org/arch/riscv/hwprobe.html>.
- *The GNU C Library*, luku Tunables (`glibc.cpu.hwcaps`).
  <https://www.gnu.org/software/libc/manual/>.
- *DWARF Debugging Information Format*, versio 5, luku 6.4 (Call Frame
  Information). <https://dwarfstd.org/>.

Kirjoja ja artikkeleita:

- Granlund, T. ja Montgomery, P.: *Division by Invariant Integers using
  Multiplication*. PLDI 1994. Vakiolla jakamisen menetelmä, jota GCC
  käyttää.
- Warren, H.: *Hacker's Delight*, 2. painos. Addison-Wesley 2012.
  Bittioperaatiot ja jako vakiolla.
- Agner Fog: *Optimizing subroutines in assembly language* ja
  käskytaulukot. <https://www.agner.org/optimize/>.
- Compiler Explorer. <https://godbolt.org/>.

Tämä tutoriaali on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
-lisenssillä (CC BY-SA 4.0). Esimerkkikoodit ovat saman lisenssin
alaisia.
