# RTL-suunnittelu SystemVerilogilla

Tiivis suomenkielinen johdatus synteesikelpoisen digitaalilogiikan
kuvaamiseen SystemVerilogilla. Esitietona on taito *Digitaalitekniikka*.
Valmis dokumentti: [rtl-suunnittelu.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rtl-suunnittelu.pdf) ja
pikaopas [rtl-suunnittelu-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rtl-suunnittelu-pikaopas.pdf).

## Sisältö

1. Johdanto – HDL:n ajattelutapa, standardit, työkalut, ensimmäinen
   suunnitelma ja testipenkki
2. Moduulit ja hierarkia – portit, parametrit, instanssit, `generate`
3. Tyypit ja lausekkeet – `logic`, vektorit, `enum`, `struct packed`,
   leveys- ja etumerkkisäännöt, paketit ja funktiot
4. Kombinaatiologiikka – `always_comb`, `unique case`, jokerit
   (`case inside`), salvat, ALU
5. Sekvenssilogiikka – `always_ff`, ei-estävä sijoitus, siirtorekisterit
6. Tilakoneet – kelvollinen/valmis-kättely, kaksi- ja
   yksiprosessityyli, UART-lähetin, vaimennin
7. Datapolut ja parametrointi – kellon sallinta, PWM, liukuhihna,
   vastapaine ja skid-puskuri, `interface`, LFSR
8. Muistit ja FIFOt – RAM- ja ROM-päättely, FIFO, rekisteripankki
9. Kellot ja nollaukset – asynkroninen ja synkroninen nollaus,
   nollauksen tahdistin
10. Kellotusalueiden ylitys – tahdistimet, kättely, asynkroninen FIFO
11. Synteesikelpoisuus ja koodaustyyli – täydelliset haarat,
    kombinatoriset silmukat, lint
12. Verilog-2005-yhteensopivuus – erot, implisiittiset johdot, muunnos
13. Testit Pythonilla: cocotb – ajurit, monitorit, viitemalli,
    parametrit ja mutaatiot
14. Lopuksi – nyrkkisäännöt, mallit ja lähteet

## Rakentaminen

```text
make testaa   # tarkistaa rakenteen, kääntää ja ajaa esimerkit (Verilator)
make pdf      # rakentaa tutoriaalin ja pikaoppaan PDF:t
```

Ajoituskaaviot tuotetaan simulaatiosta: `make -C esimerkit` tarkistaa
ne ja `make -C esimerkit paivita` kirjoittaa ne uudelleen.

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
