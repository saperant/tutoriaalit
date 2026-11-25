# Mikrokontrollerit ja bare-metal-ohjelmointi

Tiivis suomenkielinen tutoriaali mikrokontrollerin ohjelmoinnista
ilman käyttöjärjestelmää Cortex-M:llä: muistikartta, käynnistyskoodi ja
linkkeriskripti, muistiin kuvatut rekisterit, keskeytykset ja ajastimet,
jaettu data, virransäästö, viat ja debuggaus. Valmiit dokumentit:
[mikrokontrollerit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/mikrokontrollerit.pdf)
ja pikaopas
[mikrokontrollerit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/mikrokontrollerit-pikaopas.pdf).

## Sisältö

1. Johdanto – laboratorio: QEMU, Cortex-M3 ja `arm-none-eabi-gcc`
2. Cortex-M-arkkitehtuuri – rekisterit, tilat, MSP ja PSP, muistikartta,
   poikkeukset ja poikkeuskehys
3. Käynnistyskoodi ja linkkeriskripti – vektoritaulu, `.data` ja
   `.bss`, VMA ja LMA, `.noinit`
4. Muistiin kuvatut rekisterit ja GPIO – `volatile`, rakenteet,
   bittioperaatiot, bit-band, UART-ajuri
5. Keskeytykset ja NVIC – prioriteetit, sisäkkäisyys, ketjutus, BASEPRI,
   SVC ja prosessipino
6. Ajastimet – SysTick, ylivuoto, oheislaitteen ajastin, PWM ja
   kaappaus, A/D-muunnoksen laukaisu, vahtikoira
7. Yhteinen data – kadonnut päivitys, kriittinen osio, LDREX/STREX,
   rengaspuskuri
8. Virransäästötilat – WFI ja kadonnut herätys, WFE, tikitön uni
9. Viat ja vikakäsittelijät – CFSR, kehys, MPU, tuotannon vikaraportti
10. Debuggaus – SWD, gdb-palvelimet, katko- ja vahtipisteet, QEMU
11. Bare-metal-ohjelman rakenne – tapahtumajono, tilakone, testaus
    isäntäkoneella
12. Lopuksi – nyrkkisäännöt, oikeaan laitteeseen, jatkotaidot, lähteet

## Esimerkit

`esimerkit/NN-nimi/main.c` ovat Cortex-M3-ohjelmia QEMU:n
`mps2-an385`-kortille, ja `esimerkit/yhteinen/` sisältää niiden
käynnistyskoodin, linkkeriskriptin, rekisterimäärittelyt,
UART-konsolin ja rengaspuskurin. Jokaisen ohjelman tuloste ja
paluuarvo verrataan tiedostoon `esimerkit/testit/<nimi>.odotettu`.
Lisäksi tilakoneen logiikka testataan isäntäkoneella ja gdb-istunto
(`10-gdb/istunto.gdb`) ajetaan ja tarkistetaan, jos `gdb-multiarch`
on asennettu.

## Rakentaminen

```text
make testaa   # rakenne ja esimerkit (esimerkit/Makefile)
make pdf      # tutoriaali ja pikaopas
```

Tarvitaan `gcc-arm-none-eabi`, `libnewlib-arm-none-eabi`,
`qemu-system-arm` ja `gdb-multiarch`; kehityskontissa
(`.devcontainer/mikrokontrollerit`) ne ovat valmiina. Luvun 8 kuva
tuotetaan komennolla `make kuvat` (Matplotlib); kuva on
versionhallinnassa.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
