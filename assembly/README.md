# Assembly

Tiivis suomenkielinen johdatus konekieleen x86-64:llä ja RISC-V:llä
rinnakkain: kääntäjän tuottaman koodin lukeminen, kutsukonventiot,
järjestelmäkutsut ja SIMD. Valmis dokumentti:
[assembly.pdf](https://saperant.github.io/tutoriaalit/materiaalit/assembly.pdf),
pikaopas
[assembly-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/assembly-pikaopas.pdf).

## Sisältö

1. Johdanto – miksi konekieltä, työkalut, AT&T- ja Intel-syntaksi,
   ensimmäinen ohjelma ja sen tavut
2. Rekisterit, muisti ja osoitusmuodot – rekisterien osat,
   tavujärjestys, tietueiden kentät
3. Aritmetiikka ja liput – kantoluku ja ylivuoto, etumerkki, siirrot,
   jakolasku
4. Hypyt, ehdot ja silmukat – vertailut, välitarkistus, ehdollinen
   siirto
5. Pino ja kutsukonventiot – System V AMD64 ja RISC-V psABI, pinon
   tasaus, takaisinkutsut
6. C-rakenteet konekielenä – `-O0` ja `-O2`, taulukot, tietueet,
   `switch`-hyppytaulu, linkitetty lista
7. x86-64 ja RISC-V rinnakkain – sama algoritmi, CISC ja RISC,
   muistimallit
8. Järjestelmäkutsut ilman C-kirjastoa – `syscall` ja `ecall`, `_start`
9. SIMD-käskyjen perusteet – SSE2, AVX2 ja RISC-V:n vektorilaajennus
10. Kokonainen esimerkki: Adler-32 – viitetoteutus, testivektorit,
    debuggaus
11. Lopuksi – nyrkkisäännöt, mallit, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # kokoaa ja ajaa esimerkit x86-64:llä ja RISC-V:llä (QEMU)
make pdf      # rakentaa assembly.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat GCC 14:n, RISC-V-ristikääntäjän
(`gcc-riscv64-linux-gnu`, `libc6-dev-riscv64-cross`) ja QEMU:n
käyttäjätilan emulaattorin (`qemu-user`). Kehityskontti on
hakemistossa `.devcontainer/assembly/`.
