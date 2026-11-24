# Laiteohjelmiston takaisinmallinnus

Tiivis suomenkielinen tutoriaali sulautetun laitteen laiteohjelmiston
purkamisesta, analysoinnista ja emuloinnista (ARM Cortex-M, QEMU).
Aiheina laiteohjelmistokuvien rakenne ja purku, arkkitehtuurin ja
muistikartan tunnistaminen, ARM- ja Thumb-koodin lukeminen, funktioiden
ja algoritmien tunnistus, kääntäjän tuottamat rakenteet, debug-
rajapinnat sekä emulointi QEMU:lla ja Unicornilla. Kaikki kohteet ovat
paketin itse kääntämiä, kuvitteellisen LT-100-laitteen omia kuvia.

**Vastuulauseke.** Materiaali on tarkoitettu oppimiseen ja
ammatilliseen, puolustavaan työhön (oman laitteen ylläpito, vianetsintä,
yhteentoimivuus, tietoturva-auditointi). Tekniikoita saa soveltaa vain
omiin laitteisiin ja ohjelmistoihin tai kohteisiin, joihin on lupa.
Dekompilointi on sallittua tekijänoikeuslain ja EU:n
ohjelmistodirektiivin rajoissa (ks. luku 1). Muokattu radiolaite ei
välttämättä ole enää vaatimustenmukainen. Tietoturvaheikkouksista
ilmoitetaan vastuullisesti valmistajalle. Tekijät eivät vastaa
väärinkäytöstä.

Valmis dokumentti:
[laiteohjelmiston-takaisinmallinnus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/laiteohjelmiston-takaisinmallinnus.pdf),
pikaopas
[laiteohjelmiston-takaisinmallinnus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/laiteohjelmiston-takaisinmallinnus-pikaopas.pdf).

## Sisältö

1. Johdanto – käyttötarkoitukset, vastuulauseke ja laki, työkalut
2. Laiteohjelmistokuvien rakenne ja purku – muodot, otsakkeet,
   tarkisteet, entropia, säiliön purku
3. Arkkitehtuurin ja muistikartan tunnistaminen – vektoritaulu,
   latausosoite, oheislaitteet
4. ARM- ja Thumb-koodin lukeminen – Thumb-2, AAPCS, literaalivarannot,
   radare2, Capstone
5. Funktioiden ja kirjastojen tunnistaminen – kutsupuu, allekirjoitukset,
   algoritmit vakioista
6. Kääntäjän tuottamat rakenteet – tietuetaulukot, hyppytaulut
7. Debug-rajapinnat – sarjakonsoli, JTAG/SWD, gdb, debug-lukitus
8. Emulointi QEMU:lla – koko kortti, protokolla, toistettavuus
9. Emulointi Unicornilla – yksittäiset funktiot, tarkisteet ja salaus
10. Ammatilliset käyttötapaukset – suorituskyky, rikki käännös,
    tietoturva-auditointi
11. Lopuksi – puolustuksen yhteenveto, Ghidra, miten jatkaa, lähteet

## Rakentaminen

```text
make testaa   # rakentaa laitteen, ajaa analyysit ja vertaa tulosteet
make pdf      # rakentaa PDF:n ja pikaoppaan
```

Esimerkit tarvitsevat arm-none-eabi-gcc:n, QEMU:n (qemu-system-arm),
gdb-multiarchin, radare2:n, GNU binutilsin, ShellCheckin ja Pythonin
(`ruff`, `mypy`, `unicorn`, `capstone`). Laitteen rakentaa
`esimerkit/laite/Makefile`, ja analyysit ovat hakemistoja
`esimerkit/NN-nimi/`, joissa `aja.sh` ajaa analyysin ja vertaa
tulosteen tiedostoon `odotettu`. `esimerkit/testaa.sh` ajaa ne.
Kehityskontti on hakemistossa
`.devcontainer/laiteohjelmiston-takaisinmallinnus`.

Kaikki kohteet ovat paketin omia ohjelmia. Luvussa 1 ovat
takaisinmallinnuksen lailliset ja eettiset rajat.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
