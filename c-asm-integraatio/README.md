# C ja assembly yhteen

Suomenkielinen taitopaketti siitä, miten C ja konekieli toimivat
yhdessä GCC:llä x86-64:llä ja RISC-V:llä: erilliset assembly-tiedostot,
inline-assembly, kääntäjän sisäiset funktiot ja SIMD C:stä sekä
toteutuksen valinta ajon aikana. Valmis dokumentti:
[c-asm-integraatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/c-asm-integraatio.pdf),
pikaopas
[c-asm-integraatio-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/c-asm-integraatio-pikaopas.pdf).

Esitietona on *Assembly*-tutoriaali (rekisterit, kutsukonventioiden
perusteet, SIMD-käskyjen perusajatus), jonka asioita ei toisteta.

## Sisältö

1. Johdanto – kolme tapaa yhdistää C ja assembly, työkalut ja
   esimerkkien rakenne
2. Kutsusopimus rajapintana – yhteinen otsake, argumenttien
   laajennus ja `char`in etumerkki, rekisterivahti, säilyvien
   rekisterien ja pinon tasauksen rikkomisen seuraukset
3. Assembly-tiedostot projektissa – `.S` ja `.s`, symbolien
   näkyvyys, `.note.GNU-stack`, CFI-direktiivit ja pinonpurku,
   käännösjärjestelmät
4. Inline-assembly – tulosteet, syötteet, rajoitteet, sotkettavat,
   `volatile`; puuttuva `"memory"` ja `&` `-O2`:lla
5. Kääntäjän sisäiset funktiot ja SIMD – `__builtin_*`, SSE2 ja
   RISC-V:n vektorilaajennus, testaus skalaariversiota vastaan,
   automaattinen vektorointi
6. Ominaisuuksien tunnistus ajon aikana – `cpuid` ja `xgetbv`,
   `__builtin_cpu_supports`, `target`-attribuutti, ifunc, molempien
   polkujen testaus QEMU:lla, RISC-V:n `hwprobe`
7. Milloin assemblyä ei kannata kirjoittaa – jako vakiolla, asm
   optimoijan mustana laatikkona, piilokustannukset
8. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit x86-64:llä ja RISC-V:llä (QEMU)
make pdf      # rakentaa c-asm-integraatio.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat GCC 14:n, RISC-V-ristikääntäjän
(`gcc-riscv64-linux-gnu`, `libc6-dev-riscv64-cross`) ja QEMU:n
käyttäjätilan emulaattorit (`qemu-user`). Kehityskontti on
hakemistossa `.devcontainer/c-asm-integraatio/`.
