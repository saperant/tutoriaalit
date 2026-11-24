# Objektitiedostot, linkitys ja ABI

Tiivis suomenkielinen tutoriaali siitä, mitä kääntäjän jälkeen
tapahtuu: ELF-tiedostot, symbolit ja relokaatiot, staattinen ja
dynaaminen linkitys, kirjastojen versiointi, linkkeriskriptit,
ohjelman käynnistys, ABI ja virheenjäljitystieto Linuxilla
(x86-64, GNU binutils, glibc). Valmis dokumentti:
[binaarit-ja-linkitys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/binaarit-ja-linkitys.pdf),
pikaopas
[binaarit-ja-linkitys-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/binaarit-ja-linkitys-pikaopas.pdf).

## Sisältö

1. Johdanto – miksi linkitys, työkalut, esimerkkien rakenne
2. Käännöksestä ohjelmaksi – vaiheet, objektitiedosto, ELF-otsake
3. ELF-tiedoston rakenne – osiot ja segmentit, `.bss`, RELRO
4. Symbolit – paikallinen, globaali ja heikko, `-fno-common`
5. Relokaatiot – `objdump -dr`, laskukaava, ajonaikaiset relokaatiot
6. Staattinen linkitys ja arkistot – järjestys, linkkerikartta,
   kaksoismäärittely
7. Jaetut kirjastot ja hakupolut – `NEEDED`, `RUNPATH`, `$ORIGIN`
8. Paikkariippumaton koodi, GOT ja PLT – näkyvyys, laiska ja välitön
   sidonta
9. Kirjastojen versiointi – soname, ABI-rikot, symboliversiot
10. Symbolien sidonta ajon aikana – törmäykset, `LD_PRELOAD`, `dlopen`
11. Linkkeriskriptit ja muistikartat – osiorekisteri, `INSERT`, oma
    skripti
12. Ohjelman käynnistys – `ld.so`, `_start`, alustusten järjestys,
    aputaulukko
13. ABI – tyyppien koot, rakenteiden asettelu, C++:n nimet ja
    `extern "C"`
14. Virheenjäljitystieto – DWARF, `addr2line`, erillinen debug-tiedosto
15. Lopuksi – nyrkkisäännöt, vianetsintä, lähteet

## Rakentaminen

```text
make testaa   # ajaa esimerkit ja vertaa tulosteet tiedostoihin odotettu
make pdf      # rakentaa binaarit-ja-linkitys.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat GCC 14:n (`gcc-14`, `g++-14`), GNU binutilsin
ja ShellCheckin. Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`,
jonka skripti `aja.sh` kääntää, linkittää ja tutkii tulokset;
`esimerkit/testaa.sh` ajaa ne kaikki ja vertaa tulosteita. Kehityskontti
on hakemistossa `.devcontainer/binaarit-ja-linkitys`.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
